"""Android SSL Pinning 绕过工具"""
import asyncio
import subprocess
from typing import List, Optional

from android_proxy_mcp.android.adb_client import ADB_CLIENT


class SSLPinningBypass:
    """SSL Pinning 绕过工具"""

    def __init__(self, serial: str):
        self.serial = serial

    async def bypass_with_frida(self, package_name: str) -> bool:
        """
        使用 Frida 进行 SSL Pinning 绕过

        Args:
            package_name: 目标应用包名

        Returns:
            是否成功注入脚本
        """
        try:
            # 检查 Frida 是否可用
            if not await self._is_frida_available():
                return False

            # 启动 Frida 服务器（如果尚未启动）
            if not await self._is_frida_server_running():
                if not await self._start_frida_server():
                    return False

            # 注入 Frida 脚本
            script = await self._get_ssl_unpinning_script()
            if await self._inject_frida_script(package_name, script):
                return True
        except Exception as e:
            pass
        return False

    async def bypass_with_magisk(self) -> bool:
        """
        使用 Magisk 模块进行 SSL Pinning 绕过

        Returns:
            是否成功安装并启用模块
        """
        try:
            # 检查设备是否已 Root
            if not await self._is_device_rooted():
                return False

            # 检查 Magisk 是否可用
            if not await self._is_magisk_available():
                return False

            # 安装并启用 TrustMeAlready 或 JustTrustMe 模块
            return await self._install_magisk_module()
        except Exception as e:
            pass
        return False

    async def bypass_with_xposed(self, package_name: str) -> bool:
        """
        使用 Xposed/LSPosed 模块进行 SSL Pinning 绕过

        Args:
            package_name: 目标应用包名

        Returns:
            是否成功绕过
        """
        try:
            # 检查设备是否已 Root 并且 Xposed/LSPosed 已安装
            if not await self._is_device_rooted():
                return False

            if not await self._is_xposed_available():
                return False

            # 检查是否已安装 SSL Unpinning 模块
            if not await self._is_ssl_unpinning_module_installed():
                return False

            # 激活模块
            return await self._activate_ssl_unpinning_module(package_name)
        except Exception as e:
            pass
        return False

    async def _is_frida_available(self) -> bool:
        """检查 Frida 是否可用"""
        try:
            result = subprocess.run(
                ["frida", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except Exception as e:
            return False

    async def _is_frida_server_running(self) -> bool:
        """检查 Frida 服务器是否正在运行"""
        try:
            result = ADB_CLIENT.shell(self.serial, "ps | grep frida-server")
            return "frida-server" in result
        except Exception as e:
            return False

    async def _start_frida_server(self) -> bool:
        """启动 Frida 服务器"""
        try:
            # 检查设备架构
            arch = ADB_CLIENT.shell(self.serial, "getprop ro.product.cpu.abi")
            arch = arch.strip()

            # 下载并启动对应架构的 Frida 服务器
            # 这里需要根据设备架构下载对应的 frida-server 版本
            # 为简化实现，暂时返回 False
            return False
        except Exception as e:
            return False

    async def _get_ssl_unpinning_script(self) -> str:
        """获取 SSL Unpinning Frida 脚本"""
        # 这是一个简化的 SSL Unpinning 脚本
        # 实际使用中，应该使用更完善的脚本，如 frida-unpinning
        return """
        Java.perform(function() {
            // 针对 OkHttp 的 SSL Pinning 绕过
            var OkHttpClient = Java.use('okhttp3.OkHttpClient');
            if (OkHttpClient) {
                OkHttpClient.Builder.prototype.build.implementation = function() {
                    var builder = this;
                    // 移除证书固定
                    builder = builder.certificatePinner(null);
                    return builder.build.call(builder);
                };
            }

            // 针对其他常见 HTTP 客户端的绕过代码
            // ...
        });
        """

    async def _inject_frida_script(self, package_name: str, script: str) -> bool:
        """注入 Frida 脚本到目标进程"""
        try:
            # 使用 frida -U -f 命令注入脚本
            process = subprocess.Popen(
                ["frida", "-U", "-f", package_name, "-l", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=script)

            return "Attached" in stdout
        except Exception as e:
            return False

    async def _is_device_rooted(self) -> bool:
        """检查设备是否已 Root"""
        try:
            result = ADB_CLIENT.shell(self.serial, "su -c id")
            return "uid=0" in result
        except Exception as e:
            return False

    async def _is_magisk_available(self) -> bool:
        """检查 Magisk 是否可用"""
        try:
            result = ADB_CLIENT.shell(self.serial, "which magisk")
            return result.strip() != ""
        except Exception as e:
            return False

    async def _install_magisk_module(self) -> bool:
        """安装 SSL Unpinning Magisk 模块"""
        try:
            # 这里可以下载并安装 TrustMeAlready 或 JustTrustMe 模块
            # 为简化实现，暂时返回 False
            return False
        except Exception as e:
            return False

    async def _is_xposed_available(self) -> bool:
        """检查 Xposed/LSPosed 是否可用"""
        try:
            result = ADB_CLIENT.shell(self.serial, "ls /data/adb/modules | grep -i lsposed")
            return result.strip() != ""
        except Exception as e:
            return False

    async def _is_ssl_unpinning_module_installed(self) -> bool:
        """检查是否已安装 SSL Unpinning 模块"""
        try:
            result = ADB_CLIENT.shell(self.serial, "ls /data/adb/modules | grep -i sslunpin")
            return result.strip() != ""
        except Exception as e:
            return False

    async def _activate_ssl_unpinning_module(self, package_name: str) -> bool:
        """激活 SSL Unpinning 模块"""
        try:
            # 为简化实现，暂时返回 False
            return False
        except Exception as e:
            return False

    async def list_available_methods(self) -> List[str]:
        """
        列出可用的 SSL Pinning 绕过方法

        Returns:
            可用方法列表
        """
        methods = []
        if await self._is_frida_available():
            methods.append("frida")
        if await self._is_device_rooted():
            if await self._is_magisk_available():
                methods.append("magisk")
            if await self._is_xposed_available():
                if await self._is_ssl_unpinning_module_installed():
                    methods.append("xposed")
        return methods
