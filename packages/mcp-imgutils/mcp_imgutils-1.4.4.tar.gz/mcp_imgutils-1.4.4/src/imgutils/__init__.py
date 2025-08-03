"""
MCP图片工具服务

让LLM可以访问和分析本地图片的MCP服务。
"""

from .server import get_server, view_image

__all__ = ["get_server", "view_image"]
