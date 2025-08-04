"""
配置管理模块
"""

import os
from typing import Dict, Optional
from .protocols.base import ProviderConfig


class ConfigManager:
    """配置管理器"""
    
    def __init__(self):
        self._providers: Dict[str, ProviderConfig] = {}
        self._defaults: Dict[str, str] = {
            "text_to_text": "openai",
            "text_to_image": "openai",
            "text_to_audio": "edge"
        }
        # 供应商到协议实现的映射
        self._provider_protocol_map: Dict[str, str] = {}
        
        # 初始化默认配置
        self._init_default_configs()
    
    def _init_default_configs(self):
        """初始化默认配置"""
        # OpenAI默认配置
        openai_config = ProviderConfig(
            base_url="https://api.openai.com/v1",
            api_key=os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY"),
            default_models={
                "text_to_text": "gpt-4o",
                "text_to_image": "dall-e-3"
            },
            supported_protocols=["text_to_text", "text_to_image"]
        )
        self.add_provider("openai", openai_config)
        
        # Google默认配置
        google_config = ProviderConfig(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            api_key=os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY"),
            default_models={
                "text_to_text": "gemini-2.0-flash",
                "text_to_image": "gemini-2.0-flash-preview-image-generation"
            },
            supported_protocols=["text_to_text", "text_to_image"]
        )
        self.add_provider("google", google_config)
        
        # Ollama默认配置
        ollama_config = ProviderConfig(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # Ollama不需要API密钥，但OpenAI客户端需要一个值
            default_models={
                "text_to_text": "gemma3:1b",
                "text_to_image": "dall-e-3"
            },
            supported_protocols=["text_to_text"]
        )
        # Ollama使用OpenAI协议实现
        self.add_provider("ollama", ollama_config, "openai")
        
        # Edge TTS默认配置
        edge_config = ProviderConfig(
            base_url="",  # Edge TTS不需要base_url
            api_key="",  # Edge TTS不需要API密钥
            default_models={
                "text_to_audio": "zh-CN-XiaoxiaoNeural"
            },
            supported_protocols=["text_to_audio"]
        )
        self.add_provider("edge", edge_config)

        # modelscope
        modelscope_config = ProviderConfig(
            base_url="",
            api_key=os.environ.get("MODELSCOPE_API_KEY", "YOUR_MODELSCOPE_API_KEY"),
            default_models={
                "text_to_image": "MAILAND/majicflus_v1",
            },
            supported_protocols=["text_to_image"]
        )
        self.add_provider("modelscope", modelscope_config)
    
    def add_provider(self, name: str, config: ProviderConfig, protocol_impl: str = None):
        """
        添加供应商配置
        
        Args:
            name: 供应商名称
            config: 供应商配置
            protocol_impl: 使用的协议实现，默认与供应商同名
        """
        self._providers[name] = config
        # 如果没有指定协议实现，默认使用与供应商同名的协议实现
        self._provider_protocol_map[name] = protocol_impl if protocol_impl else name
    
    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """
        获取供应商配置
        
        Args:
            name: 供应商名称
            
        Returns:
            供应商配置或None
        """
        return self._providers.get(name)
    
    def get_provider_names(self) -> list:
        """
        获取所有供应商名称
        
        Returns:
            供应商名称列表
        """
        return list(self._providers.keys())
    
    def get_default_provider(self, protocol: str) -> str:
        """
        获取协议的默认供应商
        
        Args:
            protocol: 协议名称
            
        Returns:
            默认供应商名称
        """
        return self._defaults.get(protocol, "openai")
    
    def set_default_provider(self, protocol: str, provider: str):
        """
        设置协议的默认供应商
        
        Args:
            protocol: 协议名称
            provider: 供应商名称
        """
        self._defaults[protocol] = provider
    
    def get_provider_protocol_impl(self, provider: str) -> str:
        """
        获取供应商使用的协议实现
        
        Args:
            provider: 供应商名称
            
        Returns:
            协议实现名称
        """
        return self._provider_protocol_map.get(provider, provider)
    
    def update_provider_key(self, provider_name: str, api_key: str):
        """
        更新供应商的API密钥
        
        Args:
            provider_name: 供应商名称
            api_key: 新的API密钥
        """
        if provider_name in self._providers:
            config = self._providers[provider_name]
            config.api_key = api_key
            self._providers[provider_name] = config