"""iOS设备管理工具"""
from typing import List, Optional

from android_proxy_mcp.devices import DEVICE_MANAGER, DeviceInfo, DevicePlatform, BaseDevice


async def ios_list_devices() -> dict:
    """
    列出连接的iOS设备

    Returns:
        设备信息字典
    """
    try:
        devices = await DEVICE_MANAGER.refresh_devices()
        ios_devices = [d for d in devices if d.get_info().platform == DevicePlatform.IOS]

        device_info_list = []
        for device in ios_devices:
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


async def ios_get_device_info(serial: str) -> dict:
    """
    获取iOS设备详细信息

    Args:
        serial: 设备序列号

    Returns:
        设备信息字典
    """
    try:
        device_info = await DEVICE_MANAGER.get_device_info(serial)
        if device_info and device_info.platform == DevicePlatform.IOS:
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
                "error": "Device not found or not an iOS device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def ios_setup_proxy(serial: str, host: str, port: int) -> dict:
    """
    在iOS设备上设置代理

    Args:
        serial: 设备序列号
        host: 代理服务器地址
        port: 代理服务器端口

    Returns:
        设置结果
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.IOS:
            success = await device.setup_proxy(host, port)
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
        else:
            return {
                "success": False,
                "error": "Device not found or not an iOS device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def ios_clear_proxy(serial: str) -> dict:
    """
    清除iOS设备上的代理设置

    Args:
        serial: 设备序列号

    Returns:
        清除结果
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.IOS:
            success = await device.clear_proxy()
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
        else:
            return {
                "success": False,
                "error": "Device not found or not an iOS device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def ios_is_proxy_enabled(serial: str) -> dict:
    """
    检查iOS设备上的代理是否已启用

    Args:
        serial: 设备序列号

    Returns:
        代理状态
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.IOS:
            is_enabled = await device.is_proxy_enabled()
            return {
                "success": True,
                "is_enabled": is_enabled
            }
        else:
            return {
                "success": False,
                "error": "Device not found or not an iOS device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def ios_install_ca_cert(serial: str, cert_path: str) -> dict:
    """
    在iOS设备上安装CA证书

    Args:
        serial: 设备序列号
        cert_path: 证书文件路径

    Returns:
        安装结果
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.IOS:
            success = await device.install_ca_cert(cert_path)
            if success:
                return {
                    "success": True,
                    "message": f"CA certificate installed successfully on device {serial}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to install CA certificate"
                }
        else:
            return {
                "success": False,
                "error": "Device not found or not an iOS device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
