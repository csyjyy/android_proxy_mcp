"""SSL相关工具"""
from typing import List, Optional

from android_proxy_mcp.devices import DEVICE_MANAGER, DeviceInfo, DevicePlatform, BaseDevice


async def ssl_pinning_bypass(serial: str, package_name: str, method: str = "auto") -> dict:
    """
    绕过应用的SSL Pinning

    Args:
        serial: 设备序列号
        package_name: 目标应用包名
        method: 绕过方法（auto, frida, magisk, xposed）

    Returns:
        绕过结果
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.ANDROID:
            success = await device.bypass_ssl_pinning(package_name, method)
            if success:
                return {
                    "success": True,
                    "message": f"SSL Pinning bypassed successfully for {package_name}"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to bypass SSL Pinning"
                }
        else:
            return {
                "success": False,
                "error": "Device not found or not an Android device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def list_ssl_pinning_bypass_methods(serial: str) -> dict:
    """
    列出可用的SSL Pinning绕过方法

    Args:
        serial: 设备序列号

    Returns:
        可用方法列表
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.ANDROID:
            methods = await device.list_ssl_pinning_bypass_methods()
            return {
                "success": True,
                "methods": methods,
                "count": len(methods)
            }
        else:
            return {
                "success": False,
                "error": "Device not found or not an Android device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def inject_system_cert(serial: str, cert_path: str) -> dict:
    """
    注入系统证书（需要Root）

    Args:
        serial: 设备序列号
        cert_path: 证书文件路径

    Returns:
        注入结果
    """
    try:
        device = await DEVICE_MANAGER.get_device_by_serial(serial)
        if device and device.get_info().platform == DevicePlatform.ANDROID:
            success = await device.inject_system_cert(cert_path)
            if success:
                return {
                    "success": True,
                    "message": "System certificate injected successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to inject system certificate"
                }
        else:
            return {
                "success": False,
                "error": "Device not found or not an Android device"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
