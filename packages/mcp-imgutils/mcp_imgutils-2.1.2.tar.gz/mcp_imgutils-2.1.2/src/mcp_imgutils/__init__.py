"""
MCP图片工具服务

让LLM可以访问和分析本地图片和网络图片的MCP服务。
"""

import sys

import click

from .server import get_server, view_image
from .server import main as server_main


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="传输类型：stdio(标准输入输出)或sse(服务器发送事件)",
)
@click.option("--port", default=8000, help="SSE模式时使用的HTTP端口号")
def cli(transport: str, port: int) -> None:
    """运行MCP图片工具服务"""
    sys.exit(server_main(transport, port))


def main():
    """命令行入口函数"""
    cli()


__all__ = ["get_server", "view_image", "main"]
