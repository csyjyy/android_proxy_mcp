"""设备管理器 - 负责设备检测和管理"""
import asyncio
from typing import List, Optional

from android_proxy_mcp.android.adb_client import ADB_CLIENT

from .base_device import BaseDevice, DeviceInfo, DevicePlatform
from .android_device import AndroidDevice
from .ios_device import IOSDevice


class DeviceManager:
    """设备管理器"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._devices: List[BaseDevice] = []

    async def refresh_devices(self) -> List[BaseDevice]:
        """刷新设备列表"""
        self._devices = []

        # 检测Android设备
        android_devices = await self._detect_android_devices()
        self._devices.extend(android_devices)

        # 检测iOS设备
        ios_devices = await self._detect_ios_devices()
        self._devices.extend(ios_devices)

        return self._devices

    async def _detect_android_devices(self) -> List[BaseDevice]:
        """检测Android设备"""
        devices = []
        try:
            adb_devices = ADB_CLIENT.list_devices()
            for serial in adb_devices:
                device = AndroidDevice(serial)
                devices.append(device)
        except Exception as e:
            pass
        return devices

    async def _detect_ios_devices(self) -> List[BaseDevice]:
        """检测iOS设备"""
        devices = []
        try:
            from android_proxy_mcp.ios.usbmuxd_client import USBMuxdClient
            ios_serials = await USBMuxdClient.list_devices()
            for serial in ios_serials:
                device = IOSDevice(serial)
                devices.append(device)
        except Exception as e:
            pass
        return devices

    async def get_device_by_serial(self, serial: str) -> Optional[BaseDevice]:
        """
        根据序列号获取设备

        Args:
            serial: 设备序列号

        Returns:
            设备实例或None
        """
        for device in self._devices:
            if device.serial == serial:
                return device
        return None

    async def get_device_info(self, serial: str) -> Optional[DeviceInfo]:
        """
        获取设备详细信息

        Args:
            serial: 设备序列号

        Returns:
            设备信息或None
        """
        device = await self.get_device_by_serial(serial)
        if device:
            return await device.get_info()
        return None

    async def list_devices_info(self) -> List[DeviceInfo]:
        """
        获取所有设备的信息列表

        Returns:
            设备信息列表
        """
        info_list = []
        for device in self._devices:
            info = await device.get_info()
            info_list.append(info)
        return info_list

    async def setup_proxy_on_device(self, serial: str, host: str, port: int) -> bool:
        """
        在指定设备上设置代理

        Args:
            serial: 设备序列号
            host: 代理服务器地址
            port: 代理服务器端口

        Returns:
            是否成功设置代理
        """
        device = await self.get_device_by_serial(serial)
        if device:
            return await device.setup_proxy(host, port)
        return False

    async def clear_proxy_on_device(self, serial: str) -> bool:
        """
        清除指定设备上的代理设置

        Args:
            serial: 设备序列号

        Returns:
            是否成功清除代理
        """
        device = await self.get_device_by_serial(serial)
        if device:
            return await device.clear_proxy()
        return False


# 全局设备管理器实例
DEVICE_MANAGER = DeviceManager()
