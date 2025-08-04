"""
图片生成器基类模块

定义标准化的图片生成器接口，为多模型支持提供统一的抽象层。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from mcp import types


class GenerationStatus(Enum):
    """生成状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenerationResult:
    """图片生成结果"""
    status: GenerationStatus
    image_data: Optional[bytes] = None
    image_url: Optional[str] = None
    local_path: Optional[str] = None
    prompt_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """是否生成成功"""
        return self.status == GenerationStatus.COMPLETED and (
            self.image_data is not None or 
            self.image_url is not None or 
            self.local_path is not None
        )


@dataclass
class GeneratorConfig:
    """生成器配置基类"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3
    debug: bool = False
    
    def is_valid(self) -> bool:
        """验证配置是否有效"""
        return self.api_key is not None


class ImageGenerator(ABC):
    """图片生成器抽象基类"""
    
    def __init__(self, config: GeneratorConfig):
        """
        初始化生成器
        
        Args:
            config: 生成器配置
        """
        self.config = config
        self._validate_config()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """生成器名称"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """生成器显示名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """生成器描述"""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> GenerationResult:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            **kwargs: 模型特定的参数
            
        Returns:
            GenerationResult: 生成结果
            
        Raises:
            ValueError: 参数无效
            RuntimeError: 生成失败
        """
        pass
    
    @abstractmethod
    def get_tool_definition(self) -> types.Tool:
        """
        获取MCP工具定义
        
        Returns:
            types.Tool: MCP工具定义
        """
        pass
    
    @abstractmethod
    def get_supported_parameters(self) -> Dict[str, Any]:
        """
        获取支持的参数列表
        
        Returns:
            Dict[str, Any]: 参数名称和描述的映射
        """
        pass
    
    def _validate_config(self) -> None:
        """
        验证配置
        
        Raises:
            ValueError: 配置无效
        """
        if not self.config.is_valid():
            raise ValueError(f"{self.name} generator configuration is invalid")
    
    def _create_error_result(self, error_message: str) -> GenerationResult:
        """
        创建错误结果
        
        Args:
            error_message: 错误消息
            
        Returns:
            GenerationResult: 错误结果
        """
        return GenerationResult(
            status=GenerationStatus.FAILED,
            error_message=error_message
        )
    
    def _create_success_result(
        self,
        image_data: Optional[bytes] = None,
        image_url: Optional[str] = None,
        local_path: Optional[str] = None,
        prompt_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        创建成功结果
        
        Args:
            image_data: 图片二进制数据
            image_url: 图片URL
            local_path: 本地文件路径
            prompt_path: 提示词文件路径
            metadata: 元数据
            
        Returns:
            GenerationResult: 成功结果
        """
        return GenerationResult(
            status=GenerationStatus.COMPLETED,
            image_data=image_data,
            image_url=image_url,
            local_path=local_path,
            prompt_path=prompt_path,
            metadata=metadata
        )


class GeneratorError(Exception):
    """生成器错误基类"""
    
    def __init__(self, message: str, generator_name: str = "unknown"):
        self.message = message
        self.generator_name = generator_name
        super().__init__(f"[{generator_name}] {message}")


class ConfigurationError(GeneratorError):
    """配置错误"""
    pass


class GenerationError(GeneratorError):
    """生成错误"""
    pass


class APIError(GeneratorError):
    """API错误"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, generator_name: str = "unknown"):
        self.status_code = status_code
        super().__init__(message, generator_name)
