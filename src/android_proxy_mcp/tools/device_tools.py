"""设备管理工具"""
from typing import List, Optional

from android_proxy_mcp.devices import DEVICE_MANAGER, DeviceInfo, DevicePlatform, BaseDevice


async def list_devices() -> dict:
    """
    列出所有连接的设备（Android/iOS）

    Returns:
        设备信息字典
    """
    try:
        devices = await DEVICE_MANAGER.refresh_devices()

        device_info_list = []
        for device in devices:
            info = await device.get_info()
            device_info_list.append({
                "serial": info.serial,
                "platform": info.platform.value,
                "model": info.model,
                "version": info.version,
                "is_online": info.is_online,
                "device_name": info.device_name,
                "manufacturer": info.manufacturer
            })

        return {
            "success": True,
            "devices": device_info_list,
            "count": len(device_info_list)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def get_device_info(serial: str) -> dict:
    """
    获取设备详细信息

    Args:
        serial: 设备序列号

    Returns:
        设备信息字典
    """
    try:
        device_info = await DEVICE_MANAGER.get_device_info(serial)
        if device_info:
            return {
                "success": True,
                "device": {
                    "serial": device_info.serial,
                    "platform": device_info.platform.value,
                    "model": device_info.model,
                    "version": device_info.version,
                    "is_online": device_info.is_online,
                    "device_name": device_info.device_name,
                    "manufacturer": device_info.manufacturer
                }
            }
        else:
            return {
                "success": False,
                "error": "Device not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def setup_proxy(serial: str, host: str, port: int) -> dict:
    """
    在设备上设置代理

    Args:
        serial: 设备序列号
        host: 代理服务器地址
        port: 代理服务器端口

    Returns:
        设置结果
    """
    try:
        success = await DEVICE_MANAGER.setup_proxy_on_device(serial, host, port)
        if success:
            return {
                "success": True,
                "message": f"Proxy configured successfully on device {serial}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to configure proxy"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def clear_proxy(serial: str) -> dict:
    """
    清除设备上的代理设置

    Args:
        serial: 设备序列号

    Returns:
        清除结果
    """
    try:
        success = await DEVICE_MANAGER.clear_proxy_on_device(serial)
        if success:
            return {
                "success": True,
                "message": f"Proxy cleared successfully on device {serial}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to clear proxy"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def is_proxy_enabled(serial: str) -> dict:
    """
    检查设备上的代理是否已启用

    Args:
        serial: 设备序列号

    Returns:
        代理状态
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device:
            is_enabled = await device.is_proxy_enabled()
            return {
                "success": True,
                "is_enabled": is_enabled
            }
        else:
            return {
                "success": False,
                "error": "Device not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
