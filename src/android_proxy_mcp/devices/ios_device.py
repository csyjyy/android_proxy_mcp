"""iOS设备实现"""
from .base_device import BaseDevice, DeviceInfo, DevicePlatform
from android_proxy_mcp.ios.usbmuxd_client import USBMuxdClient
from android_proxy_mcp.ios.network_config import NetworkConfig
from android_proxy_mcp.ios.cert_installer import CertInstaller


class IOSDevice(BaseDevice):
    """iOS设备实现类"""

    def __init__(self, serial: str):
        super().__init__(serial)
        self.cert_installer = CertInstaller(serial)

    async def get_info(self) -> DeviceInfo:
        """获取设备信息"""
        return await USBMuxdClient.get_device_info(self.serial)

    async def setup_proxy(self, host: str, port: int) -> bool:
        """设置代理"""
        try:
            return await NetworkConfig.set_http_proxy(self.serial, host, port)
        except Exception as e:
            return False

    async def clear_proxy(self) -> bool:
        """清除代理设置"""
        try:
            return await NetworkConfig.clear_proxy(self.serial)
        except Exception as e:
            return False

    async def is_proxy_enabled(self) -> bool:
        """检查代理是否已启用"""
        try:
            proxy_config = await NetworkConfig.get_proxy_config(self.serial)
            return proxy_config["http"]["enabled"] or proxy_config["https"]["enabled"]
        except Exception as e:
            return False

    async def install_ca_cert(self, cert_path: str) -> bool:
        """
        安装CA证书到iOS设备

        Args:
            cert_path: 证书文件路径

        Returns:
            是否成功安装证书
        """
        try:
            return await self.cert_installer.install_ca_cert(cert_path)
        except Exception as e:
            return False
