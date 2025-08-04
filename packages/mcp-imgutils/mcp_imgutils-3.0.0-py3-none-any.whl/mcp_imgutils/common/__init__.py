"""
通用模块

提供错误处理、资源管理等通用功能。
"""

from .errors import BFLError, get_error_message

__all__ = ["BFLError", "get_error_message"]
