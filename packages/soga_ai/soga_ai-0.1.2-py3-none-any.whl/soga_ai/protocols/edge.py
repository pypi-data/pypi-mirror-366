"""
Edge协议实现（使用edge-tts库进行文本转音频）
"""

import os
import hashlib
from typing import Optional
import edge_tts
from .base import Protocol, ProviderConfig
from ..decorators import register_protocol


@register_protocol("edge")
class EdgeProtocol(Protocol):
    """Edge协议实现（使用edge-tts库进行文本转音频）"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
    
    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Edge协议不支持文本到文本转换，抛出NotImplementedError
        
        Args:
            prompt: 输入文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Raises:
            NotImplementedError: Edge协议不支持文本到文本转换
        """
        raise NotImplementedError("Edge协议不支持文本到文本转换")
    
    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard") -> str:
        """
        Edge协议不支持文本到图像转换，抛出NotImplementedError
        
        Args:
            prompt: 输入文本
            model: 模型名称
            size: 图像尺寸
            quality: 图像质量
            
        Raises:
            NotImplementedError: Edge协议不支持文本到图像转换
        """
        raise NotImplementedError("Edge协议不支持文本到图像转换")
    
    async def _text_to_audio_async(self, prompt: str, voice: str = "zh-CN-XiaoxiaoNeural", 
                                   rate: str = "+0%", volume: str = "+0%", 
                                   save_path: Optional[str] = None) -> str:
        """
        异步文本到音频转换
        
        Args:
            prompt: 输入文本
            voice: 语音名称
            rate: 语速调整
            volume: 音量调整
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的音频文件路径
        """
        # 如果没有指定保存路径，则生成默认路径
        if save_path is None:
            # 生成文件名
            hash_object = hashlib.md5(prompt.encode())
            filename = f"edge_{voice}_{hash_object.hexdigest()[:8]}.mp3"
            
            # 确保audio目录存在
            audio_dir = "audio"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir)
                
            filepath = os.path.join(audio_dir, filename)
        else:
            filepath = save_path
            # 确保保存路径的目录存在
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
        
        # 使用edge-tts生成音频
        communicate = edge_tts.Communicate(text=prompt, voice=voice, rate=rate, volume=volume)
        await communicate.save(filepath)
        
        return filepath
    
    def text_to_audio(self, prompt: str, model: Optional[str] = None,
                      voice: str = "zh-CN-XiaoxiaoNeural", speed: float = 1.0,
                      save_path: Optional[str] = None) -> str:
        """
        使用edge-tts库进行文本到音频转换，并保存到文件
        
        Args:
            prompt: 输入文本
            model: 模型名称（在Edge TTS中对应语音）
            voice: 语音名称，默认为中文女声
            speed: 语速，1.0为正常速度
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的音频文件路径
        """
        import asyncio
        
        if model is None:
            model = self.config.default_models.get("text_to_audio", voice)
        
        # 将速度转换为edge-tts格式 (+0% for 1.0, +25% for 1.25, -25% for 0.75, etc.)
        # 限制在edge-tts支持的范围内 (-50% 到 +100%)
        rate_value = max(-50, min(100, int((speed - 1.0) * 100)))
        rate_percent = f"{rate_value:+d}%" if rate_value != 0 else "+0%"
        
        # 运行异步函数
        return asyncio.run(self._text_to_audio_async(prompt, model, rate_percent, save_path=save_path))