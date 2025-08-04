"""
BFL FLUX 框架生成器

基于新框架的BFL FLUX生成器实现，包装现有的BFL功能。
"""

import os
from typing import Any, Dict

from mcp import types

from ..base import ImageGenerator, GeneratorConfig, GenerationResult
from .config import FluxModel, DEFAULT_MODEL, PRESET_SIZES
from .generator import generate_image_bfl as legacy_generate_image_bfl


class BFLFrameworkConfig(GeneratorConfig):
    """BFL框架配置"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 从环境变量获取API密钥
        if not self.api_key:
            self.api_key = os.getenv("BFL_API_KEY")
        
        # 设置默认base_url
        if not self.base_url:
            self.base_url = "https://api.bfl.ai/v1"


class BFLFrameworkGenerator(ImageGenerator):
    """BFL FLUX框架生成器"""
    
    def __init__(self, config: BFLFrameworkConfig):
        """初始化BFL生成器"""
        super().__init__(config)
        self.default_model = DEFAULT_MODEL
        self.preset_sizes = PRESET_SIZES
    
    @property
    def name(self) -> str:
        """生成器名称"""
        return "bfl"
    
    @property
    def display_name(self) -> str:
        """生成器显示名称"""
        return "BFL FLUX"
    
    @property
    def description(self) -> str:
        """生成器描述"""
        return "Black Forest Labs FLUX模型图片生成器，支持flux-dev, flux-pro, flux-pro-1.1, flux-pro-1.1-ultra"
    
    async def generate(self, prompt: str, **kwargs) -> GenerationResult:
        """
        生成图片
        
        Args:
            prompt: 图片描述提示词
            **kwargs: 支持的参数：
                - model: FluxModel 或 str
                - width: int
                - height: int  
                - preset_size: str
                
        Returns:
            GenerationResult: 生成结果
        """
        try:
            # 构造参数字典，模拟原有的MCP工具调用
            arguments = {
                "prompt": prompt,
                **kwargs
            }
            
            # 调用现有的BFL生成器
            result = await legacy_generate_image_bfl("generate_image_bfl", arguments)
            
            # 解析结果
            if result and len(result) > 0:
                text_content = result[0]
                if hasattr(text_content, 'text') and "✅ 图片生成成功" in text_content.text:
                    # 从文本中提取路径信息
                    local_path = self._extract_local_path(text_content.text)
                    txt_path = self._extract_txt_path(text_content.text)
                    
                    return self._create_success_result(
                        local_path=local_path,
                        prompt_path=txt_path,
                        metadata={
                            "model": kwargs.get("model", self.default_model.value),
                            "prompt": prompt
                        }
                    )
                else:
                    # 生成失败
                    error_msg = text_content.text if hasattr(text_content, 'text') else "未知错误"
                    return self._create_error_result(error_msg)
            else:
                return self._create_error_result("生成器返回空结果")
                
        except Exception as e:
            return self._create_error_result(f"BFL生成失败: {str(e)}")
    
    def get_tool_definition(self) -> types.Tool:
        """获取MCP工具定义"""
        return types.Tool(
            name="generate_image_bfl",
            description="使用BFL FLUX模型生成高质量图片",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "图片描述文本（建议使用英文以获得最佳效果）"
                    },
                    "model": {
                        "type": "string",
                        "enum": [model.value for model in FluxModel],
                        "description": f"FLUX模型选择，默认: {self.default_model.value}",
                        "default": self.default_model.value
                    },
                    "preset_size": {
                        "type": "string",
                        "enum": list(self.preset_sizes.keys()) + ["default"],
                        "description": "预设尺寸选择"
                    },
                    "width": {
                        "type": "integer",
                        "minimum": 32,
                        "maximum": 2048,
                        "description": "自定义图片宽度（如果不使用preset_size）"
                    },
                    "height": {
                        "type": "integer", 
                        "minimum": 32,
                        "maximum": 2048,
                        "description": "自定义图片高度（如果不使用preset_size）"
                    }
                },
                "required": ["prompt"]
            }
        )
    
    def get_supported_parameters(self) -> Dict[str, Any]:
        """获取支持的参数列表"""
        return {
            "model": {
                "type": "enum",
                "values": [model.value for model in FluxModel],
                "default": self.default_model.value,
                "description": "FLUX模型选择"
            },
            "preset_size": {
                "type": "enum", 
                "values": list(self.preset_sizes.keys()) + ["default"],
                "description": "预设尺寸选择"
            },
            "width": {
                "type": "integer",
                "range": [32, 2048],
                "description": "自定义图片宽度"
            },
            "height": {
                "type": "integer",
                "range": [32, 2048], 
                "description": "自定义图片高度"
            }
        }
    
    def _extract_local_path(self, text: str) -> str:
        """从结果文本中提取本地路径"""
        import re
        match = re.search(r"LOCAL_PATH::本地路径::.*?::(.+?)(?:\n|$)", text)
        return match.group(1) if match else ""
    
    def _extract_txt_path(self, text: str) -> str:
        """从结果文本中提取提示词文件路径"""
        import re
        match = re.search(r"📝 提示词已保存到: (.+?)(?:\n|$)", text)
        return match.group(1) if match else ""
