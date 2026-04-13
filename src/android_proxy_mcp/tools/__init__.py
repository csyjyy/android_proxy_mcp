"""MCP 工具模块"""

from .android_tools import (
    android_clear_proxy,
    android_get_device_info,
    android_list_devices,
    android_setup_proxy,
)
from .ios_tools import (
    ios_list_devices,
    ios_get_device_info,
    ios_setup_proxy,
    ios_clear_proxy,
    ios_is_proxy_enabled,
    ios_install_ca_cert,
)
from .device_tools import (
    list_devices,
    get_device_info,
    setup_proxy,
    clear_proxy,
    is_proxy_enabled,
)
from .ssl_tools import (
    ssl_pinning_bypass,
    list_ssl_pinning_bypass_methods,
    inject_system_cert,
)
from .proxy_tools import get_cert_info
from .traffic_tools import (
    proxy_status,
    traffic_clear,
    traffic_get_detail,
    traffic_list,
    traffic_read_body,
    traffic_search,
)
# Frida tools
from .frida_tools import (
    frida_status,
    frida_get_session_keys,
    frida_decrypt,
    frida_encrypt,
    frida_bypass,
)
# UI automation tools
from .ui_tools import (
    ui_dump,
    ui_tap,
    ui_tap_by_label,
    ui_input_text,
    ui_input_by_label,
)
# Autonomous automation tools
from .autonomous_tools import (
    autonomous_decrypt_all_captured_traffic,
    run_autonomous_sequence,
)

__all__ = [
    # Proxy tools
    "get_cert_info",
    "proxy_status",
    # Traffic tools
    "traffic_list",
    "traffic_get_detail",
    "traffic_search",
    "traffic_read_body",
    "traffic_clear",
    # Android tools
    "android_list_devices",
    "android_get_device_info",
    "android_setup_proxy",
    "android_clear_proxy",
    # iOS tools
    "ios_list_devices",
    "ios_get_device_info",
    "ios_setup_proxy",
    "ios_clear_proxy",
    "ios_is_proxy_enabled",
    "ios_install_ca_cert",
    # Device tools
    "list_devices",
    "get_device_info",
    "setup_proxy",
    "clear_proxy",
    "is_proxy_enabled",
    # SSL tools
    "ssl_pinning_bypass",
    "list_ssl_pinning_bypass_methods",
    "inject_system_cert",
    # Frida tools
    "frida_status",
    "frida_get_session_keys",
    "frida_decrypt",
    "frida_encrypt",
    "frida_bypass",
    # UI automation
    "ui_dump",
    "ui_tap",
    "ui_tap_by_label",
    "ui_input_text",
    "ui_input_by_label",
    # Autonomous automation
    "autonomous_decrypt_all_captured_traffic",
    "run_autonomous_sequence",
]
