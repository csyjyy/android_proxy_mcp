/**
 * 云闪付自动化安全测试 Frida 脚本
 * 
 * 功能：
 * 1. 绕过梆梆加固 Frida 检测（5个检测点 NOP）
 * 2. Hook 原生层会话密钥生成（UPNSACryptUtil::randomSessionKey）
 * 3. Hook Java层解密方法（sm4DecryptMsgWithSK）直接打印明文
 * 4. 导出 Frida RPC 服务：encrypt() / decrypt()，使用APP原生加解密
 * 5. 将会话密钥记录到文件供后续解密流量使用
 */

// =============================================
// 1. 梆梆绕过 - NOP 检测函数
// =============================================

function nopFunc(addr) {
    Memory.protect(addr, 4, 'rwx');
    var writer = new Arm64Writer(addr);
    writer.putRet();
    writer.flush();
    writer.dispose();
}

function bypass_detect_func() {
    var base = Module.findBaseAddress("libDexHelper.so");
    if (!base) {
        console.log("[!] libDexHelper.so not found");
        return;
    }
    console.log("[+] libDexHelper.so base: " + base);
    
    // 云闪付 10.2.9+ 五个检测点偏移
    nopFunc(base.add(0x4e9d8));
    nopFunc(base.add(0x4b614));
    nopFunc(base.add(0x557f4));
    nopFunc(base.add(0x5afa8));
    nopFunc(base.add(0x4f884));
    
    console.log("[+] Bypassed 5 detection points (NOP applied)");
}

// =============================================
// 2. Hook 原生会话密钥生成
// =============================================

var sessionKeys = [];

function hookSessionKeyGeneration() {
    const moduleName = "libencrypt.so";
    var base = Module.findBaseAddress(moduleName);
    if (!base) {
        console.log("[!] " + moduleName + " not found");
        return;
    }
    console.log("[+] " + moduleName + " base: " + base);
    
    // UPNSACryptUtil::randomSessionKey @ +0x5eb98
    const addrUPNSA = base.add(0x5eb98);
    // UPXCryptUtil::randomSessionKey @ +0x5b7c8
    const addrUPX = base.add(0x5b7c8);
    
    Interceptor.attach(addrUPNSA, {
        onEnter: function(args) {
            this.length = args[1].toInt32();
            this.outputPtr = args[2];
            console.log("\n[Native] UPNSACryptUtil::randomSessionKey called");
        },
        onLeave: function(retval) {
            const charPtr = this.outputPtr.readPointer();
            if (!charPtr.isNull()) {
                const sessionKey = charPtr.readUtf8String();
                console.log("    [+] 🔑 GENERATED SESSION KEY: " + sessionKey);
                sessionKeys.push({
                    timestamp: Date.now(),
                    key: sessionKey,
                    type: 'UPNSA'
                });
                
                // Save to file on device (pull later)
                try {
                    const file = new File("/sdcard/unionpay_session_keys.txt", "a");
                    if (file) {
                        file.write(sessionKey + "\n");
                        file.flush();
                        file.close();
                    }
                } catch (e) {
                    // Ignore if can't write
                }
            }
        }
    });
    
    Interceptor.attach(addrUPX, {
        onEnter: function(args) {
            this.length = args[1].toInt32();
            this.outputPtr = args[2];
        },
        onLeave: function(retval) {
            const charPtr = this.outputPtr.readPointer();
            if (!charPtr.isNull()) {
                const sessionKey = charPtr.readUtf8String();
                console.log("[UPX] 🔑 GENERATED SESSION KEY: " + sessionKey);
                sessionKeys.push({
                    timestamp: Date.now(),
                    key: sessionKey,
                    type: 'UPX'
                });
                
                try {
                    const file = new File("/sdcard/unionpay_session_keys.txt", "a");
                    if (file) {
                        file.write(sessionKey + "\n");
                        file.flush();
                        file.close();
                    }
                } catch (e) {
                }
            }
        }
    });
    
    console.log("[+] Session key hooks installed");
}

// =============================================
// 3. Hook Java层方法，直接获取解密明文
// =============================================

function hookJavaMethods() {
    Java.perform(function() {
        console.log("\n[+] Installing Java hooks...");
        try {
            // Try both possible IJniInterface locations
            var ijniClassNames = [
                "com.unionpay.encrypt.IJniInterface",
                "com.unionpay.utils.IJniInterface"
            ];
            
            for (var i = 0; i < ijniClassNames.length; i++) {
                try {
                    var ijniInterface = Java.use(ijniClassNames[i]);
                    
                    // 捕获makeNSASessionKey返回，和原生输出对比
                    if (ijniInterface.makeNSASessionKey) {
                        ijniInterface.makeNSASessionKey.implementation = function() {
                            var result = this.makeNSASessionKey();
                            console.log("\n[Java] makeNSASessionKey() returned: " + result);
                            return result;
                        };
                        console.log("[+] Hooked makeNSASessionKey in " + ijniClassNames[i]);
                    }
                    
                    // 捕获sm4EncryptMsgWithSK，看明文
                    if (ijniInterface.sm4EncryptMsgWithSK && ijniInterface.sm4EncryptMsgWithSK.overload) {
                        var overload = ijniInterface.sm4EncryptMsgWithSK.overload('java.lang.String');
                        if (overload) {
                            overload.implementation = function(plaintext) {
                                console.log("\n[Java] sm4EncryptMsgWithSK(String plaintext)");
                                console.log("    Plaintext: " + plaintext);
                                var ciphertext = this.sm4EncryptMsgWithSK(plaintext);
                                console.log("    Ciphertext: " + ciphertext);
                                return ciphertext;
                            };
                            console.log("[+] Hooked sm4EncryptMsgWithSK in " + ijniClassNames[i]);
                        }
                    }
                    
                    // 捕获sm4DecryptMsgWithSK，直接看解密后的明文
                    if (ijniInterface.sm4DecryptMsgWithSK && ijniInterface.sm4DecryptMsgWithSK.overload) {
                        var overload = ijniInterface.sm4DecryptMsgWithSK.overload('java.lang.String');
                        if (overload) {
                            overload.implementation = function(ciphertext) {
                                console.log("\n[Java] sm4DecryptMsgWithSK(String ciphertext)");
                                console.log("    Ciphertext: " + ciphertext);
                                var plaintext = this.sm4DecryptMsgWithSK(ciphertext);
                                console.log("    🔓 DECRYPTED: " + plaintext);
                                return plaintext;
                            };
                            console.log("[+] Hooked sm4DecryptMsgWithSK in " + ijniClassNames[i]);
                        }
                    }
                    
                    console.log("[+] ✅ Java hooks installed for " + ijniClassNames[i]);
                } catch (e) {
                    // Class not found, try next
                }
            }
        } catch (e) {
            console.error("[-] Error in Java.perform: " + e);
            console.error(e.stack);
        }
    });
}

// =============================================
// 4. 导出 RPC 服务供电脑端调用原生加解密
// =============================================

rpc.exports = {
    encrypt: function(message) {
        return new Promise(function(resolve) {
            Java.perform(function() {
                try {
                    // Try both possible class locations
                    var classNames = [
                        "com.unionpay.utils.IJniInterface",
                        "com.unionpay.encrypt.IJniInterface"
                    ];
                    var success = false;
                    
                    for (var i = 0; i < classNames.length; i++) {
                        try {
                            var ijniInterface = Java.use(classNames[i]);
                            var ciphertext = ijniInterface.c(message);
                            resolve(ciphertext);
                            success = true;
                            break;
                        } catch (e) {
                            // continue
                        }
                    }
                    
                    if (!success) {
                        console.error("[-] RPC encrypt: IJniInterface not found");
                        resolve(null);
                    }
                } catch (e) {
                    console.error("[-] RPC encrypt error: " + e);
                    resolve(null);
                }
            });
        });
    },
    
    decrypt: function(ciphertext) {
        return new Promise(function(resolve) {
            Java.perform(function() {
                try {
                    var classNames = [
                        "com.unionpay.utils.IJniInterface",
                        "com.unionpay.encrypt.IJniInterface"
                    ];
                    var success = false;
                    
                    for (var i = 0; i < classNames.length; i++) {
                        try {
                            var ijniInterface = Java.use(classNames[i]);
                            var plaintext = ijniInterface.d(ciphertext);
                            resolve(plaintext);
                            success = true;
                            break;
                        } catch (e) {
                            // continue
                        }
                    }
                    
                    if (!success) {
                        console.error("[-] RPC decrypt: IJniInterface not found");
                        resolve(null);
                    }
                } catch (e) {
                    console.error("[-] RPC decrypt error: " + e);
                    resolve(null);
                }
            });
        });
    },
    
    getcapturedsessionkeys: function() {
        return new Promise(function(resolve) {
            resolve(sessionKeys.map(function(sk) {
                return {
                    timestamp: sk.timestamp,
                    key: sk.key,
                    type: sk.type
                };
            }));
        });
    },
    
    bypass: function() {
        return new Promise(function(resolve) {
            bypass_detect_func();
            hookSessionKeyGeneration();
            hookJavaMethods();
            resolve(true);
        });
    }
};

// =============================================
// 5. dlopen hook - wait for libraries to load
// =============================================

function hook_dlopen() {
    const funcName = "android_dlopen_ext";
    var funcPtr = Module.findExportByName(null, funcName);
    if (funcPtr !== null) {
        Interceptor.attach(funcPtr, {
            onEnter: function (args) {
                this.pathPtr = args[0];
                if (this.pathPtr !== null) {
                    try {
                        var path = this.pathPtr.readCString();
                        if (path.indexOf("libDexHelper.so") !== -1) {
                            this.isLibDexHelper = true;
                        }
                        if (path.indexOf("libencrypt.so") !== -1) {
                            this.isLibEncrypt = true;
                        }
                    } catch (e) {
                        console.log("[!] Error reading path");
                    }
                }
            },
            onLeave: function (retval) {
                if (this.isLibDexHelper) {
                    console.log("[+] libDexHelper.so loaded, applying bypass...");
                    bypass_detect_func();
                }
                if (this.isLibEncrypt) {
                    console.log("[+] libencrypt.so loaded, installing hooks...");
                    setTimeout(function() {
                        hookSessionKeyGeneration();
                        hookJavaMethods();
                    }, 500);
                }
            }
        });
        console.log("[+] Hooked android_dlopen_ext");
    } else {
        console.log("[!] android_dlopen_ext not found, waiting 2s for libraries...");
        setTimeout(function() {
            bypass_detect_func();
            hookSessionKeyGeneration();
            hookJavaMethods();
        }, 2000);
    }
}

// =============================================
// Entry point
// =============================================

function main() {
    console.log("=".repeat(70));
    console.log("云闪付 UnionPay Autonomous Security Testing");
    console.log("Bangcle Bypass + Session Key Capture + RPC Encrypt/Decrypt");
    console.log("=".repeat(70));
    
    // Check if already loaded
    var baseDex = Module.findBaseAddress("libDexHelper.so");
    var baseEncrypt = Module.findBaseAddress("libencrypt.so");
    
    if (baseDex !== null) {
        console.log("[+] libDexHelper.so already loaded, applying bypass...");
        bypass_detect_func();
    }
    if (baseEncrypt !== null) {
        console.log("[+] libencrypt.so already loaded, installing hooks...");
        hookSessionKeyGeneration();
        hookJavaMethods();
    }
    
    hook_dlopen();
}

setImmediate(main);
