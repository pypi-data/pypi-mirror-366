"""
MCP服务：本地图片工具

此服务允许用户提供本地图片路径，服务检查图片文件大小，
读取数据并转换为base64编码，然后发送给LLM。
"""

import contextlib
import os
import sys
from typing import Any

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .utils import (
    DEFAULT_MAX_FILE_SIZE,
    download_image_from_url,
    get_image_details,
    is_url,
    read_and_encode_image,
    validate_image_path,
)

# 全局MCP服务器实例
_server_instance = None


def get_server() -> Server:
    """
    获取MCP服务器实例（单例模式）

    Returns:
        Server: MCP服务器实例
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = Server("imgutils")
    return _server_instance


async def view_image(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    查看本地图片并将其发送给LLM进行分析

    Args:
        name: 工具名称
        arguments: 工具参数，包含image_path和可选的max_file_size

    Returns:
        包含图片内容的响应列表

    Raises:
        ValueError: 当参数无效或图片处理出错时抛出
    """
    if name != "view_image":
        raise ValueError(f"未知工具：{name}")

    if "image_path" not in arguments:
        raise ValueError("缺少必需参数 'image_path'")

    image_path = arguments["image_path"]
    max_file_size = arguments.get("max_file_size", DEFAULT_MAX_FILE_SIZE)

    # 检测是否为URL
    temp_file_path = None
    try:
        if is_url(image_path):
            # 从URL下载图片
            temp_file_path = download_image_from_url(image_path)
            actual_path = temp_file_path
        else:
            # 本地文件路径
            validate_image_path(image_path)
            actual_path = image_path

        # 检查文件大小（仅对本地文件，URL下载的图片信任MCP协议处理）
        if not is_url(image_path):
            file_size = os.path.getsize(actual_path)
            if file_size > max_file_size:
                return [
                    types.TextContent(
                        type="text",
                        text=f"图片文件太大：{file_size} 字节。最大允许大小：{max_file_size} 字节",
                    )
                ]

        try:
            # 读取并编码图片
            encoded_image, mime_type = read_and_encode_image(actual_path)

            # 获取图片详细信息
            details = get_image_details(actual_path)

            # 获取文件名（对于URL，显示原始URL）
            if is_url(image_path):
                filename = f"URL: {image_path}"
            else:
                filename = os.path.basename(image_path)

            # 解析文件大小
            file_size_str = details["文件大小"]  # "1,234 字节"
            file_size_bytes = int(file_size_str.replace(",", "").replace(" 字节", ""))
            file_size_kb = file_size_bytes / 1024
            file_size_mb = file_size_kb / 1024

            # 构建详细的文本信息
            info_text = (
                f"图片详细信息:\n"
                f"文件名: {filename}\n"
                f"文件路径: {details['文件路径']}\n"
                f"文件大小: {file_size_bytes} 字节 ({file_size_kb:.2f} KB, {file_size_mb:.2f} MB)\n"
                f"图片格式: {details['图片格式']}\n"
                f"分辨率: {details['尺寸']}\n"
                f"颜色模式: {details['颜色模式']}\n"
                f"总像素数: {details['总像素数']}\n"
            )

            # 添加EXIF数据（如果有）
            if "EXIF数据" in details and details["EXIF数据"]:
                info_text += "\nEXIF Metadata:\n"
                for key, value in details["EXIF数据"].items():
                    info_text += f"{key}: {value}\n"

            # 返回混合内容：详细信息 + 图片数据
            return [
                types.TextContent(type="text", text=info_text),
                types.ImageContent(
                    type="image", data=encoded_image, mimeType=mime_type
                ),
            ]
        except Exception as e:
            return [types.TextContent(type="text", text=f"处理图片时出错：{str(e)}")]
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                with contextlib.suppress(Exception):
                    os.unlink(temp_file_path)
    except Exception as e:
        return [types.TextContent(type="text", text=f"处理请求时出错：{str(e)}")]


async def setup_server(server: Server = None) -> Server:
    """
    设置并配置MCP服务器

    Args:
        server: 可选的Server实例，如果为None则创建新实例

    Returns:
        配置好的MCP服务器实例
    """
    if server is None:
        server = get_server()

    # 注册工具处理函数
    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """根据工具名称调用相应的处理函数"""
        if name == "view_image":
            return await view_image(name, arguments)
        else:
            raise ValueError(f"未知工具：{name}")

    # 注册工具列表函数
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        """返回可用工具列表"""
        return [
            types.Tool(
                name="view_image",
                description="查看本地图片或网络图片并将其发送给LLM进行分析，包含详细的图片信息和EXIF元数据",
                inputSchema={
                    "type": "object",
                    "required": ["image_path"],
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "本地图片文件的完整路径或HTTP/HTTPS图片URL",
                        },
                        "max_file_size": {
                            "type": "integer",
                            "description": f"可选，图片文件的最大大小（字节），默认{DEFAULT_MAX_FILE_SIZE}字节（仅适用于本地文件）",
                        },
                    },
                },
            )
        ]

    return server


async def run_server(transport: str = "stdio", port: int = 8000) -> None:
    """
    运行MCP服务器

    Args:
        transport: 传输类型，'stdio'或'sse'
        port: 如果使用'sse'传输时的端口号
    """
    server = await setup_server()

    if transport == "sse":
        # SSE传输实现
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.routing import Mount, Route

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await server.run(
                    streams[0], streams[1], server.create_initialization_options()
                )

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        import uvicorn

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        # 标准输入/输出传输实现
        print("启动MCP图片工具服务器...", file=sys.stderr)
        async with stdio_server() as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )


def main(transport: str = "stdio", port: int = 8000) -> int:
    """
    主函数

    Args:
        transport: 传输类型，'stdio'或'sse'
        port: 如果使用'sse'传输时的端口号

    Returns:
        退出码
    """
    try:
        anyio.run(run_server, transport, port)
        return 0
    except KeyboardInterrupt:
        print("MCP服务器已停止", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"MCP服务器运行错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
