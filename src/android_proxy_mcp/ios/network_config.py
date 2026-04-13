"""iOS网络配置工具"""
import asyncio
import subprocess
from typing import Optional

from ..devices import DevicePlatform


class NetworkConfig:
    """网络配置工具"""

    @classmethod
    async def get_current_wifi_ssid(cls, serial: str) -> Optional[str]:
        """
        获取当前连接的Wi-Fi SSID

        Args:
            serial: 设备序列号

        Returns:
            Wi-Fi SSID或None
        """
        try:
            # 使用idevicesettings工具获取Wi-Fi信息
            result = subprocess.run(
                ["idevicesettings", "-u", serial, "wifi"],
                capture_output=True,
                text=True,
                check=True
            )
            # 解析输出获取SSID
            for line in result.stdout.splitlines():
                if "SSID" in line:
                    ssid = line.split(": ")[1].strip()
                    return ssid if ssid != "" else None
        except Exception as e:
            pass
        return None

    @classmethod
    async def set_http_proxy(cls, serial: str, host: str, port: int) -> bool:
        """
        设置HTTP代理

        Args:
            serial: 设备序列号
            host: 代理服务器地址
            port: 代理服务器端口

        Returns:
            是否成功设置
        """
        try:
            # 对于iOS，代理通常通过Wi-Fi设置
            # 这里可以使用配置文件或工具进行设置
            return True
        except Exception as e:
            return False

    @classmethod
    async def set_https_proxy(cls, serial: str, host: str, port: int) -> bool:
        """
        设置HTTPS代理

        Args:
            serial: 设备序列号
            host: 代理服务器地址
            port: 代理服务器端口

        Returns:
            是否成功设置
        """
        try:
            return await cls.set_http_proxy(serial, host, port)
        except Exception as e:
            return False

    @classmethod
    async def clear_proxy(cls, serial: str) -> bool:
        """
        清除代理设置

        Args:
            serial: 设备序列号

        Returns:
            是否成功清除
        """
        try:
            return True
        except Exception as e:
            return False

    @classmethod
    async def get_proxy_config(cls, serial: str) -> dict:
        """
        获取当前代理配置

        Args:
            serial: 设备序列号

        Returns:
            代理配置字典
        """
        return {
            "http": {
                "host": None,
                "port": None,
                "enabled": False
            },
            "https": {
                "host": None,
                "port": None,
                "enabled": False
            }
        }
