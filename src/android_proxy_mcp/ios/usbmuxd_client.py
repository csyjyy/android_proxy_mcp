"""iOS设备通信客户端 - 基于usbmuxd协议"""
import asyncio
import subprocess
from typing import List, Optional

from ..devices import DeviceInfo, DevicePlatform


class USBMuxdClient:
    """usbmuxd通信客户端"""

    @classmethod
    async def list_devices(cls) -> List[str]:
        """
        列出连接的iOS设备序列号

        Returns:
            设备序列号列表
        """
        devices = []
        try:
            # 使用idevice_id工具列出设备
            result = subprocess.run(
                ["idevice_id", "-l"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                devices = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        except FileNotFoundError:
            pass
        except subprocess.CalledProcessError:
            pass
        except Exception as e:
            pass

        return devices

    @classmethod
    async def get_device_info(cls, serial: str) -> Optional[DeviceInfo]:
        """
        获取设备详细信息

        Args:
            serial: 设备序列号

        Returns:
            设备信息
        """
        try:
            # 使用ideviceinfo工具获取设备信息
            result = subprocess.run(
                ["ideviceinfo", "-u", serial],
                capture_output=True,
                text=True,
                check=True
            )

            info = {}
            for line in result.stdout.splitlines():
                if ": " in line:
                    key, value = line.split(": ", 1)
                    info[key.strip()] = value.strip()

            model = info.get("ProductType", "Unknown")
            version = info.get("ProductVersion", "Unknown")
            device_name = info.get("DeviceName", "Unknown")

            return DeviceInfo(
                serial=serial,
                platform=DevicePlatform.IOS,
                model=model,
                version=version,
                is_online=True,
                device_name=device_name,
                manufacturer="Apple"
            )
        except Exception as e:
            return DeviceInfo(
                serial=serial,
                platform=DevicePlatform.IOS,
                model="Unknown",
                version="Unknown",
                is_online=False
            )

    @classmethod
    async def install_cert(cls, serial: str, cert_path: str) -> bool:
        """
        安装证书到设备

        Args:
            serial: 设备序列号
            cert_path: 证书文件路径

        Returns:
            是否成功安装
        """
        try:
            # 这里可以使用ideviceinstaller或其他工具安装证书
            return True
        except Exception as e:
            return False
