"""
通用模块

提供错误处理、配置管理、重试机制等通用功能。
"""

from .errors import (
    BFLError,
    MCPImageUtilsError,
    ConfigurationError,
    NetworkError,
    APIError,
    ValidationError,
    ResourceError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    QuotaError,
    ErrorCategory,
    ErrorSeverity,
    ErrorContext,
)
from .error_messages import get_user_message, format_error_for_user
from .config import ConfigManager, get_config_manager, get_config, set_config
from .retry import RetryConfig, RetryStrategy, with_retry
from .rate_limiter import RateLimit, RateLimiter, get_rate_limiter_manager

__all__ = [
    # 错误类型
    "BFLError",
    "MCPImageUtilsError",
    "ConfigurationError",
    "NetworkError",
    "APIError",
    "ValidationError",
    "ResourceError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "QuotaError",
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorContext",

    # 错误消息
    "get_user_message",
    "format_error_for_user",

    # 配置管理
    "ConfigManager",
    "get_config_manager",
    "get_config",
    "set_config",

    # 重试机制
    "RetryConfig",
    "RetryStrategy",
    "with_retry",

    # 速率限制
    "RateLimit",
    "RateLimiter",
    "get_rate_limiter_manager",
]


# 向后兼容的函数
def get_error_message(status_code: int, default_message: str = None) -> str:
    """
    获取错误信息 (向后兼容)

    Args:
        status_code: HTTP状态码
        default_message: 默认消息

    Returns:
        错误消息
    """
    error_messages = {
        401: "API key 无效",
        402: "积分不足",
        429: "超出并发限制",
        400: "请求参数错误",
        500: "服务器内部错误"
    }

    return error_messages.get(status_code, default_message or f"未知错误: {status_code}")
