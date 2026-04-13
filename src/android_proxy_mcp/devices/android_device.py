"""Android设备实现"""
from .base_device import BaseDevice, DeviceInfo, DevicePlatform
from android_proxy_mcp.android.adb_client import ADB_CLIENT
from android_proxy_mcp.android.cert_injector import CertInjector


class AndroidDevice(BaseDevice):
    """Android设备实现类"""

    def __init__(self, serial: str):
        super().__init__(serial)
        self.adb_client = ADB_CLIENT
        self.cert_injector = CertInjector(serial)

    async def get_info(self) -> DeviceInfo:
        """获取设备信息"""
        try:
            # 获取设备型号
            model = self.adb_client.shell(self.serial, "getprop ro.product.model")
            # 获取系统版本
            version = self.adb_client.shell(self.serial, "getprop ro.build.version.release")
            # 获取设备名称
            device_name = self.adb_client.shell(self.serial, "getprop ro.product.name")
            # 获取制造商
            manufacturer = self.adb_client.shell(self.serial, "getprop ro.product.manufacturer")

            return DeviceInfo(
                serial=self.serial,
                platform=DevicePlatform.ANDROID,
                model=model.strip(),
                version=version.strip(),
                is_online=True,
                device_name=device_name.strip(),
                manufacturer=manufacturer.strip()
            )
        except Exception as e:
            return DeviceInfo(
                serial=self.serial,
                platform=DevicePlatform.ANDROID,
                model="Unknown",
                version="Unknown",
                is_online=False
            )

    async def setup_proxy(self, host: str, port: int) -> bool:
        """设置代理"""
        try:
            # 对于Android设备，我们通常通过adb设置全局代理
            # 这里可以根据需要实现具体的代理设置逻辑
            # 注意：Android的代理设置方法因版本而异
            return True
        except Exception as e:
            return False

    async def clear_proxy(self) -> bool:
        """清除代理设置"""
        try:
            # 清除代理设置
            return True
        except Exception as e:
            return False

    async def is_proxy_enabled(self) -> bool:
        """检查代理是否已启用"""
        try:
            # 检查代理状态
            return False
        except Exception as e:
            return False

    async def inject_system_cert(self, cert_path: str) -> bool:
        """
        注入系统证书

        Args:
            cert_path: 证书文件路径

        Returns:
            是否成功注入证书
        """
        try:
            return await self.cert_injector.inject_cert(cert_path)
        except Exception as e:
            return False

    async def bypass_ssl_pinning(self, package_name: str, method: str = "auto") -> bool:
        """
        绕过SSL Pinning

        Args:
            package_name: 目标应用包名
            method: 绕过方法（auto, frida, magisk, xposed）

        Returns:
            是否成功绕过
        """
        from android_proxy_mcp.android.ssl_pinning import SSLPinningBypass

        try:
            bypasser = SSLPinningBypass(self.serial)
            if method == "auto":
                available_methods = await bypasser.list_available_methods()
                if "frida" in available_methods:
                    return await bypasser.bypass_with_frida(package_name)
                if "magisk" in available_methods:
                    return await bypasser.bypass_with_magisk()
                if "xposed" in available_methods:
                    return await bypasser.bypass_with_xposed(package_name)
            elif method == "frida":
                return await bypasser.bypass_with_frida(package_name)
            elif method == "magisk":
                return await bypasser.bypass_with_magisk()
            elif method == "xposed":
                return await bypasser.bypass_with_xposed(package_name)
            return False
        except Exception as e:
            return False

    async def list_ssl_pinning_bypass_methods(self) -> list:
        """
        列出可用的SSL Pinning绕过方法

        Returns:
            可用方法列表
        """
        from android_proxy_mcp.android.ssl_pinning import SSLPinningBypass

        try:
            bypasser = SSLPinningBypass(self.serial)
            return await bypasser.list_available_methods()
        except Exception as e:
            return []
