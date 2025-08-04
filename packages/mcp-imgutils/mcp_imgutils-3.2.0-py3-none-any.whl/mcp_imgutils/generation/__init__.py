"""
图片生成模块

提供多种模型的图片生成功能和统一的框架接口。
"""

# 框架基础
from .base import (
    ImageGenerator,
    GeneratorConfig,
    GenerationResult,
    GenerationStatus,
    GeneratorError,
    ConfigurationError,
    GenerationError,
    APIError,
)
from .registry import GeneratorRegistry, register_generator, get_registry

# BFL生成器
from .bfl.framework_generator import BFLFrameworkGenerator, BFLFrameworkConfig

# 保持向后兼容
from .bfl import generate_image_bfl
from .bfl.generator import get_bfl_tool_definition

__all__ = [
    # 框架基础
    "ImageGenerator",
    "GeneratorConfig",
    "GenerationResult",
    "GenerationStatus",
    "GeneratorError",
    "ConfigurationError",
    "GenerationError",
    "APIError",

    # 注册系统
    "GeneratorRegistry",
    "register_generator",
    "get_registry",

    # BFL生成器
    "BFLFrameworkGenerator",
    "BFLFrameworkConfig",

    # 向后兼容
    "generate_image_bfl",
    "get_bfl_tool_definition",
]


def initialize_generators():
    """初始化所有生成器"""
    registry = get_registry()

    # 注册BFL生成器
    register_generator("bfl", BFLFrameworkGenerator)

    # 尝试创建BFL生成器实例（如果配置有效）
    try:
        bfl_config = BFLFrameworkConfig()
        if bfl_config.is_valid():
            registry.create_generator("bfl", bfl_config)
    except Exception:
        # 配置无效时静默失败，用户可以稍后手动配置
        pass
