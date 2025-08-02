"""
客户端类，用于调用各种AI能力
"""

import os
from typing import Optional
from .config import ConfigManager
from .protocols.base import ProviderConfig
from .decorators import get_registered_protocols


class Client:
    """AI能力客户端"""
    
    def __init__(self, openai_api_key: str = None, google_api_key: str = None):
        """
        初始化客户端
        
        Args:
            openai_api_key: OpenAI API密钥，如果未提供则从环境变量OPENAI_API_KEY读取
            google_api_key: Google API密钥，如果未提供则从环境变量GOOGLE_API_KEY读取
        """
        self.config_manager = ConfigManager()
        self._protocols = get_registered_protocols()
        self._initialized_providers: dict = {}
        
        # 如果提供了API密钥，则更新配置
        if openai_api_key:
            self.config_manager.update_provider_key("openai", openai_api_key)
        elif os.environ.get("OPENAI_API_KEY"):
            self.config_manager.update_provider_key("openai", os.environ.get("OPENAI_API_KEY"))
            
        if google_api_key:
            self.config_manager.update_provider_key("google", google_api_key)
        elif os.environ.get("GOOGLE_API_KEY"):
            self.config_manager.update_provider_key("google", os.environ.get("GOOGLE_API_KEY"))
    
    def add_provider(self, name: str, config: ProviderConfig, protocol_impl: str = None):
        """
        添加供应商配置
        
        Args:
            name: 供应商名称
            config: 供应商配置
            protocol_impl: 使用的协议实现，默认与供应商同名
        """
        self.config_manager.add_provider(name, config, protocol_impl)
    
    def set_api_key(self, provider: str, api_key: str):
        """
        设置供应商的API密钥
        
        Args:
            provider: 供应商名称
            api_key: API密钥
        """
        self.config_manager.update_provider_key(provider, api_key)
    
    def text_to_text(self, prompt: str, provider: Optional[str] = None, 
                     model: Optional[str] = None, temperature: float = 0.7, 
                     max_tokens: int = 1000) -> str:
        """
        文本到文本转换
        
        Args:
            prompt: 输入文本
            provider: 指定供应商，如果不指定则使用默认供应商
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            生成的文本
        """
        if provider is None:
            provider = self.config_manager.get_default_provider("text_to_text")
        
        provider_config = self.config_manager.get_provider(provider)
        if not provider_config:
            raise ValueError(f"未找到供应商配置: {provider}")
        
        # 获取供应商使用的协议实现
        protocol_impl_name = self.config_manager.get_provider_protocol_impl(provider)
        
        if provider not in self._initialized_providers:
            protocol_cls = self._protocols.get(protocol_impl_name)
            if not protocol_cls:
                raise ValueError(f"未找到协议实现: {protocol_impl_name}")
            self._initialized_providers[provider] = protocol_cls(provider_config)
        
        return self._initialized_providers[provider].text_to_text(
            prompt, model, temperature, max_tokens
        )
    
    def text_to_image(self, prompt: str, provider: Optional[str] = None,
                      model: Optional[str] = None, size: str = "1024x1024",
                      quality: str = "standard", save_path: Optional[str] = None) -> str:
        """
        文本到图像转换
        
        Args:
            prompt: 输入文本
            provider: 指定供应商，如果不指定则使用默认供应商
            model: 模型名称
            size: 图像尺寸
            quality: 图像质量
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的图像文件路径
        """
        if provider is None:
            provider = self.config_manager.get_default_provider("text_to_image")
        
        provider_config = self.config_manager.get_provider(provider)
        if not provider_config:
            raise ValueError(f"未找到供应商配置: {provider}")
        
        # 获取供应商使用的协议实现
        protocol_impl_name = self.config_manager.get_provider_protocol_impl(provider)
        
        if provider not in self._initialized_providers:
            protocol_cls = self._protocols.get(protocol_impl_name)
            if not protocol_cls:
                raise ValueError(f"未找到协议实现: {protocol_impl_name}")
            self._initialized_providers[provider] = protocol_cls(provider_config)
        
        return self._initialized_providers[provider].text_to_image(
            prompt, model, size, quality, save_path
        )
    
    def text_to_audio(self, prompt: str, provider: Optional[str] = None,
                      model: Optional[str] = None, voice: str = "default",
                      speed: float = 1.0, save_path: Optional[str] = None) -> str:
        """
        文本到音频转换
        
        Args:
            prompt: 输入文本
            provider: 指定供应商，如果不指定则使用默认供应商
            model: 模型名称
            voice: 语音名称
            speed: 语速
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的音频文件路径
        """
        if provider is None:
            provider = self.config_manager.get_default_provider("text_to_audio")
        
        provider_config = self.config_manager.get_provider(provider)
        if not provider_config:
            raise ValueError(f"未找到供应商配置: {provider}")
        
        # 获取供应商使用的协议实现
        protocol_impl_name = self.config_manager.get_provider_protocol_impl(provider)
        
        if provider not in self._initialized_providers:
            protocol_cls = self._protocols.get(protocol_impl_name)
            if not protocol_cls:
                raise ValueError(f"未找到协议实现: {protocol_impl_name}")
            self._initialized_providers[provider] = protocol_cls(provider_config)
        
        # 检查协议是否支持text_to_audio方法
        if not hasattr(self._initialized_providers[provider], 'text_to_audio'):
            raise NotImplementedError(f"供应商 {provider} 不支持文本到音频转换")
        
        return self._initialized_providers[provider].text_to_audio(
            prompt, model, voice, speed, save_path
        )