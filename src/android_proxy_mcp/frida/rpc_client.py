"""
Frida RPC Client for UnionPay
Calls native encrypt/decrypt via com.unionpay.utils.IJniInterface.c() / d()
"""

import frida
from typing import Optional, List, Dict


class UnionPayRPCClient:
    def __init__(self, package_name: str = "com.unionpay.android", device: Optional[frida.Device] = None):
        self.package_name = package_name
        if device is None:
            # Try to find USB device
            device_manager = frida.get_device_manager()
            devices = device_manager.enumerate_devices()
            if devices:
                # Use first available (usually USB)
                device = devices[0]
            else:
                device = frida.get_local_device()
        self.device = device
        self.session: Optional[frida.Session] = None
        self.script: Optional[frida.Script] = None

    def attach(self, script_path: str) -> None:
        """Attach to process and load the script"""
        try:
            # Try to attach to existing process
            process = self.device.get_process(self.package_name)
            pid = process.pid
            self.session = self.device.attach(pid)
        except Exception:
            # Process not running, spawn it
            pid = self.device.spawn([self.package_name])
            self.session = self.device.attach(pid)

        # Load script
        with open(script_path, 'r') as f:
            script_source = f.read()

        self.script = self.session.create_script(script_source)
        self.script.load()

    def encrypt(self, plaintext: str) -> Optional[str]:
        """Encrypt using native IJniInterface.c(message)"""
        assert self.script is not None
        return self.script.exports.encrypt(plaintext)

    def decrypt(self, ciphertext: str) -> Optional[str]:
        """Decrypt using native IJniInterface.d(ciphertext)"""
        assert self.script is not None
        return self.script.exports.decrypt(ciphertext)

    def get_captured_session_keys(self) -> List[Dict]:
        """Get all captured session keys"""
        assert self.script is not None
        return self.script.exports.getcapturedsessionkeys()

    def bypass(self) -> bool:
        """Force apply bangcle bypass"""
        assert self.script is not None
        return self.script.exports.bypass()

    def detach(self) -> None:
        """Detach from session"""
        if self.session:
            self.session.detach()
