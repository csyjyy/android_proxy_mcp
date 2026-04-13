"""设备抽象层 - 定义所有设备的公共接口"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DevicePlatform(Enum):
    """设备平台枚举"""
    ANDROID = "android"
    IOS = "ios"


@dataclass
class DeviceInfo:
    """设备信息数据类"""
    serial: str
    platform: DevicePlatform
    model: str
    version: str
    is_online: bool
    # 其他通用属性
    device_name: Optional[str] = None
    manufacturer: Optional[str] = None


class BaseDevice(ABC):
    """设备抽象基类"""

    def __init__(self, serial: str):
        self.serial = serial

    @abstractmethod
    async def get_info(self) -> DeviceInfo:
        """获取设备信息"""
        pass

    @abstractmethod
    async def setup_proxy(self, host: str, port: int) -> bool:
        """
        设置代理

        Args:
            host: 代理服务器地址
            port: 代理服务器端口

        Returns:
            是否成功设置代理
        """
        pass

    @abstractmethod
    async def clear_proxy(self) -> bool:
        """
        清除代理设置

        Returns:
            是否成功清除代理
        """
        pass

    @abstractmethod
    async def is_proxy_enabled(self) -> bool:
        """
        检查代理是否已启用

        Returns:
            代理是否已启用
        """
        pass
