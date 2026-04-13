"""
MCP 服务入口

基于 MCP 协议的 Android 无头抓包服务。
流量数据通过 SQLite 与启动脚本共享。
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .tools import (
    android_clear_proxy,
    android_get_device_info,
    android_list_devices,
    android_setup_proxy,
    ios_list_devices,
    ios_get_device_info,
    ios_setup_proxy,
    ios_clear_proxy,
    ios_is_proxy_enabled,
    ios_install_ca_cert,
    list_devices,
    get_device_info,
    setup_proxy,
    clear_proxy,
    is_proxy_enabled,
    ssl_pinning_bypass,
    list_ssl_pinning_bypass_methods,
    inject_system_cert,
    get_cert_info,
    proxy_status,
    traffic_clear,
    traffic_get_detail,
    traffic_list,
    traffic_read_body,
    traffic_search,
    frida_status,
    frida_get_session_keys,
    frida_decrypt,
    frida_encrypt,
    frida_bypass,
    ui_dump,
    ui_tap,
    ui_tap_by_label,
    ui_input_text,
    ui_input_by_label,
    autonomous_decrypt_all_captured_traffic,
    run_autonomous_sequence,
)

# 创建 MCP 服务器
server = Server("android-proxy-mcp")


# ============== 工具定义 ==============

@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        # 设备管理工具
        Tool(
            name="list_devices",
            description="列出所有连接的设备（Android/iOS）",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_device_info",
            description="获取设备详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="setup_proxy",
            description="在设备上设置代理",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "proxy_host": {
                        "type": "string",
                        "description": "代理服务器地址",
                    },
                    "proxy_port": {
                        "type": "integer",
                        "description": "代理服务器端口，默认 8080",
                        "default": 8080,
                    },
                },
                "required": ["serial", "proxy_host"],
            },
        ),
        Tool(
            name="clear_proxy",
            description="清除设备上的代理设置",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="is_proxy_enabled",
            description="检查设备上的代理是否已启用",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        # 代理状态工具
        Tool(
            name="proxy_status",
            description=(
                "获取代理服务器状态。注意：需要先在终端运行 "
                "'uv run android-proxy-start' 启动代理。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_cert_info",
            description=(
                "获取 CA 证书信息和安装指南。抓取 HTTPS 流量需要"
                "在设备上安装此证书。"
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        # 流量工具
        Tool(
            name="traffic_list",
            description=(
                "列出捕获的 HTTP/HTTPS 流量。默认返回最近 10 条，"
                "支持分页和筛选。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "返回数量限制，默认 10，最大 10",
                        "default": 10,
                    },
                    "offset": {
                        "type": "integer",
                        "description": (
                            "跳过前 N 条记录，用于分页（如 offset=10 "
                            "查看第 11-20 条）"
                        ),
                        "default": 0,
                    },
                    "filter_domain": {
                        "type": "string",
                        "description": "按域名筛选，支持通配符（如 *.example.com）",
                    },
                    "filter_type": {
                        "type": "string",
                        "description": (
                            "按资源类型筛选（XHR, Document, Image, Script, "
                            "Stylesheet, Font, Media, Other）"
                        ),
                    },
                    "filter_status": {
                        "type": "string",
                        "description": "按状态码筛选（如 200, 4xx, 500-599）",
                    },
                    "filter_url": {
                        "type": "string",
                        "description": "按 URL 筛选，支持正则表达式",
                    },
                },
            },
        ),
        Tool(
            name="traffic_get_detail",
            description=(
                "获取单个请求的元数据（请求头、响应头、参数等）。"
                "注意：不包含请求体和响应体内容，使用 traffic_read_body 读取。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "请求 ID（从 traffic_list 获取）",
                    },
                },
                "required": ["request_id"],
            },
        ),
        Tool(
            name="traffic_search",
            description=(
                "搜索流量内容。可搜索 URL、请求头、请求体、响应头、响应体。"
                "返回匹配的片段而非完整内容。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词",
                    },
                    "search_in": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "搜索范围：url, request_headers, request_body, "
                            "response_headers, response_body, all（默认）"
                        ),
                    },
                    "method": {
                        "type": "string",
                        "description": "限定 HTTP 方法（GET/POST）",
                    },
                    "domain": {
                        "type": "string",
                        "description": "限定域名（支持通配符 %）",
                    },
                    "context_chars": {
                        "type": "integer",
                        "description": "返回匹配内容前后字符数，默认 150",
                        "default": 150,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最多返回几条匹配，默认 10",
                        "default": 10,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="traffic_read_body",
            description="分片读取请求体或响应体。用于查看大内容，支持分页读取。",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string",
                        "description": "请求 ID",
                    },
                    "field": {
                        "type": "string",
                        "description": (
                            "读取字段：request_body 或 response_body（默认）"
                        ),
                        "default": "response_body",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "起始位置，默认 0",
                        "default": 0,
                    },
                    "length": {
                        "type": "integer",
                        "description": "读取长度，默认 4000 字符",
                        "default": 4000,
                    },
                },
                "required": ["request_id"],
            },
        ),
        Tool(
            name="traffic_clear",
            description="清空所有捕获的流量",
            inputSchema={"type": "object", "properties": {}},
        ),
        # Android 工具
        Tool(
            name="android_list_devices",
            description="列出所有连接的 Android 设备",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="android_get_device_info",
            description="获取指定 Android 设备的详细信息（型号、版本、是否 root 等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号（从 android_list_devices 获取）",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="android_setup_proxy",
            description=(
                "在 Android 设备上设置 HTTP 代理。注意：此方式对部分应用"
                "可能无效，建议在 Wi-Fi 设置中手动配置。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "proxy_host": {
                        "type": "string",
                        "description": "代理服务器地址（通常是运行此服务的电脑 IP）",
                    },
                    "proxy_port": {
                        "type": "integer",
                        "description": "代理服务器端口，默认 8080",
                        "default": 8080,
                    },
                },
                "required": ["serial", "proxy_host"],
            },
        ),
        Tool(
            name="android_clear_proxy",
            description="清除 Android 设备上的代理设置",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        # iOS 工具
        Tool(
            name="ios_list_devices",
            description="列出所有连接的 iOS 设备",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="ios_get_device_info",
            description="获取指定 iOS 设备的详细信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="ios_setup_proxy",
            description="在 iOS 设备上设置 HTTP 代理",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "proxy_host": {
                        "type": "string",
                        "description": "代理服务器地址",
                    },
                    "proxy_port": {
                        "type": "integer",
                        "description": "代理服务器端口，默认 8080",
                        "default": 8080,
                    },
                },
                "required": ["serial", "proxy_host"],
            },
        ),
        Tool(
            name="ios_clear_proxy",
            description="清除 iOS 设备上的代理设置",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="ios_is_proxy_enabled",
            description="检查 iOS 设备上的代理是否已启用",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="ios_install_ca_cert",
            description="在 iOS 设备上安装 CA 证书",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "cert_path": {
                        "type": "string",
                        "description": "证书文件路径",
                    },
                },
                "required": ["serial", "cert_path"],
            },
        ),
        # SSL 工具
        Tool(
            name="ssl_pinning_bypass",
            description="绕过应用的 SSL Pinning",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "package_name": {
                        "type": "string",
                        "description": "目标应用包名",
                    },
                    "method": {
                        "type": "string",
                        "description": "绕过方法（auto, frida, magisk, xposed）",
                        "default": "auto",
                    },
                },
                "required": ["serial", "package_name"],
            },
        ),
        Tool(
            name="list_ssl_pinning_bypass_methods",
            description="列出可用的 SSL Pinning 绕过方法",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                },
                "required": ["serial"],
            },
        ),
        Tool(
            name="inject_system_cert",
            description="注入系统证书（需要 Root）",
            inputSchema={
                "type": "object",
                "properties": {
                    "serial": {
                        "type": "string",
                        "description": "设备序列号",
                    },
                    "cert_path": {
                        "type": "string",
                        "description": "证书文件路径",
                    },
                },
                "required": ["serial", "cert_path"],
            },
        ),
        # Frida 工具
        Tool(
            name="frida_status",
            description="检查 Frida 连接状态，验证脚本加载",
            inputSchema={
                "type": "object",
                "properties": {
                    "package_name": {
                        "type": "string",
                        "description": "目标应用包名，默认 com.unionpay.android",
                        "default": "com.unionpay.android",
                    },
                },
            },
        ),
        Tool(
            name="frida_get_session_keys",
            description="获取 Frida 捕获的所有会话密钥",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="frida_decrypt",
            description="使用 Frida RPC 调用原生解密，com.unionpay.utils.IJniInterface.d(ciphertext)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ciphertext": {
                        "type": "string",
                        "description": "十六进制密文",
                    },
                },
                "required": ["ciphertext"],
            },
        ),
        Tool(
            name="frida_encrypt",
            description="使用 Frida RPC 调用原生加密，com.unionpay.utils.IJniInterface.c(plaintext)",
            inputSchema={
                "type": "object",
                "properties": {
                    "plaintext": {
                        "type": "string",
                        "description": "明文",
                    },
                },
                "required": ["plaintext"],
            },
        ),
        Tool(
            name="frida_bypass",
            description="强制应用梆梆（Bangcle）Frida 检测绕过",
            inputSchema={"type": "object", "properties": {}},
        ),
        # UI 自动化工具
        Tool(
            name="ui_dump",
            description="dump 当前 UI，提取所有可交互元素（可点击/可聚焦）",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="ui_tap",
            description="点击指定 ID 的元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_id": {
                        "type": "integer",
                        "description": "元素 ID（从 ui_dump 获取）",
                    },
                },
                "required": ["element_id"],
            },
        ),
        Tool(
            name="ui_tap_by_label",
            description="点击第一个标签包含指定文字的元素（便捷方法）",
            inputSchema={
                "type": "object",
                "properties": {
                    "label_contains": {
                        "type": "string",
                        "description": "标签包含文字，大小写不敏感",
                    },
                },
                "required": ["label_contains"],
            },
        ),
        Tool(
            name="ui_input_text",
            description="点击指定 ID 的输入框，输入文字",
            inputSchema={
                "type": "object",
                "properties": {
                    "element_id": {
                        "type": "integer",
                        "description": "元素 ID（从 ui_dump 获取）",
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文字",
                    },
                },
                "required": ["element_id", "text"],
            },
        ),
        Tool(
            name="ui_input_by_label",
            description="找到标签匹配的输入框，输入文字",
            inputSchema={
                "type": "object",
                "properties": {
                    "label_contains": {
                        "type": "string",
                        "description": "标签包含文字",
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文字",
                    },
                },
                "required": ["label_contains", "text"],
            },
        ),
        # 自治自动化工具
        Tool(
            name="autonomous_decrypt_all_captured_traffic",
            description="自动批量解密所有捕获流量中找到的密文，使用 Frida RPC",
            inputSchema={
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "SQLite 数据库路径，默认 traffic.db",
                        "default": "traffic.db",
                    },
                },
            },
        ),
        Tool(
            name="run_autonomous_sequence",
            description="运行自动化操作序列，自动完成登录等流程",
            inputSchema={
                "type": "object",
                "properties": {
                    "sequence": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "操作: {type: tap_by_label, label: '...'} 或者 {type: input_by_label, label: '...', text: '...'}",
                        },
                        "description": "操作列表",
                    },
                },
                "required": ["sequence"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    result: dict[str, Any]

    # 代理工具
    if name == "proxy_status":
        result = proxy_status()
    elif name == "get_cert_info":
        result = get_cert_info()

    # 流量工具
    elif name == "traffic_list":
        result = traffic_list(
            limit=arguments.get("limit", 10),
            offset=arguments.get("offset", 0),
            filter_domain=arguments.get("filter_domain"),
            filter_type=arguments.get("filter_type"),
            filter_status=arguments.get("filter_status"),
            filter_url=arguments.get("filter_url"),
        )
    elif name == "traffic_get_detail":
        result = traffic_get_detail(arguments["request_id"])
    elif name == "traffic_search":
        result = traffic_search(
            keyword=arguments["keyword"],
            search_in=arguments.get("search_in"),
            method=arguments.get("method"),
            domain=arguments.get("domain"),
            context_chars=arguments.get("context_chars", 150),
            limit=arguments.get("limit", 10),
        )
    elif name == "traffic_read_body":
        result = traffic_read_body(
            request_id=arguments["request_id"],
            field=arguments.get("field", "response_body"),
            offset=arguments.get("offset", 0),
            length=arguments.get("length", 4000),
        )
    elif name == "traffic_clear":
        result = traffic_clear()

    # Android 工具（异步）
    elif name == "android_list_devices":
        result = await android_list_devices()
    elif name == "android_get_device_info":
        result = await android_get_device_info(arguments["serial"])
    elif name == "android_setup_proxy":
        result = await android_setup_proxy(
            serial=arguments["serial"],
            proxy_host=arguments["proxy_host"],
            proxy_port=arguments.get("proxy_port", 8080),
        )
    elif name == "android_clear_proxy":
        result = await android_clear_proxy(arguments["serial"])
    # iOS 工具（异步）
    elif name == "ios_list_devices":
        result = await ios_list_devices()
    elif name == "ios_get_device_info":
        result = await ios_get_device_info(arguments["serial"])
    elif name == "ios_setup_proxy":
        result = await ios_setup_proxy(
            serial=arguments["serial"],
            proxy_host=arguments["proxy_host"],
            proxy_port=arguments.get("proxy_port", 8080),
        )
    elif name == "ios_clear_proxy":
        result = await ios_clear_proxy(arguments["serial"])
    elif name == "ios_is_proxy_enabled":
        result = await ios_is_proxy_enabled(arguments["serial"])
    elif name == "ios_install_ca_cert":
        result = await ios_install_ca_cert(
            serial=arguments["serial"],
            cert_path=arguments["cert_path"],
        )
    # 设备管理工具（异步）
    elif name == "list_devices":
        result = await list_devices()
    elif name == "get_device_info":
        result = await get_device_info(arguments["serial"])
    elif name == "setup_proxy":
        result = await setup_proxy(
            serial=arguments["serial"],
            host=arguments["proxy_host"],
            port=arguments.get("proxy_port", 8080),
        )
    elif name == "clear_proxy":
        result = await clear_proxy(arguments["serial"])
    elif name == "is_proxy_enabled":
        result = await is_proxy_enabled(arguments["serial"])
    # SSL 工具（异步）
    elif name == "ssl_pinning_bypass":
        result = await ssl_pinning_bypass(
            serial=arguments["serial"],
            package_name=arguments["package_name"],
            method=arguments.get("method", "auto"),
        )
    elif name == "list_ssl_pinning_bypass_methods":
        result = await list_ssl_pinning_bypass_methods(arguments["serial"])
    elif name == "inject_system_cert":
        result = await inject_system_cert(
            serial=arguments["serial"],
            cert_path=arguments["cert_path"],
        )

    # Frida 工具
    elif name == "frida_status":
        from android_proxy_mcp.tools.frida_tools import frida_status
        result = frida_status(
            package_name=arguments.get("package_name", "com.unionpay.android"),
        )
    elif name == "frida_get_session_keys":
        from android_proxy_mcp.tools.frida_tools import frida_get_session_keys
        result = frida_get_session_keys()
    elif name == "frida_decrypt":
        from android_proxy_mcp.tools.frida_tools import frida_decrypt
        result = frida_decrypt(
            ciphertext=arguments["ciphertext"],
        )
    elif name == "frida_encrypt":
        from android_proxy_mcp.tools.frida_tools import frida_encrypt
        result = frida_encrypt(
            plaintext=arguments["plaintext"],
        )
    elif name == "frida_bypass":
        from android_proxy_mcp.tools.frida_tools import frida_bypass
        result = frida_bypass()

    # UI 自动化工具
    elif name == "ui_dump":
        from android_proxy_mcp.tools.ui_tools import ui_dump
        result = ui_dump()
    elif name == "ui_tap":
        from android_proxy_mcp.tools.ui_tools import ui_tap
        result = ui_tap(
            element_id=arguments["element_id"],
        )
    elif name == "ui_tap_by_label":
        from android_proxy_mcp.tools.ui_tools import ui_tap_by_label
        result = ui_tap_by_label(
            label_contains=arguments["label_contains"],
        )
    elif name == "ui_input_text":
        from android_proxy_mcp.tools.ui_tools import ui_input_text
        result = ui_input_text(
            element_id=arguments["element_id"],
            text=arguments["text"],
        )
    elif name == "ui_input_by_label":
        from android_proxy_mcp.tools.ui_tools import ui_input_by_label
        result = ui_input_by_label(
            label_contains=arguments["label_contains"],
            text=arguments["text"],
        )

    # 自治自动化工具
    elif name == "autonomous_decrypt_all_captured_traffic":
        from android_proxy_mcp.tools.autonomous_tools import autonomous_decrypt_all_captured_traffic
        result = autonomous_decrypt_all_captured_traffic(
            db_path=arguments.get("db_path", "traffic.db"),
        )
    elif name == "run_autonomous_sequence":
        from android_proxy_mcp.tools.autonomous_tools import run_autonomous_sequence
        result = run_autonomous_sequence(
            sequence=arguments["sequence"],
        )

    else:
        result = {"error": f"Unknown tool: {name}"}

    # 格式化输出
    import json
    return [
        TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )
    ]


async def run_server():
    """运行 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """入口函数"""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
