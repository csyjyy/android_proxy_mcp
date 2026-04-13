"""设备管理模块"""
from .base_device import BaseDevice, DeviceInfo, DevicePlatform
from .android_device import AndroidDevice
from .ios_device import IOSDevice
from .device_manager import DeviceManager, DEVICE_MANAGER

__all__ = [
    "BaseDevice",
    "DeviceInfo",
    "DevicePlatform",
    "AndroidDevice",
    "IOSDevice",
    "DeviceManager",
    "DEVICE_MANAGER"
]
