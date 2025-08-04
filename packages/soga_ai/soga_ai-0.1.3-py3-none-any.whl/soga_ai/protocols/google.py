"""
Google协议实现
"""

import os
import base64
import hashlib
import requests
from typing import Optional
from .base import Protocol, ProviderConfig
from ..decorators import register_protocol


@register_protocol("google")
class GoogleProtocol(Protocol):
    """Google协议实现"""
    
    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        使用Google进行文本到文本转换
        
        Args:
            prompt: 输入文本
            model: 模型名称，默认使用配置中的默认模型
            temperature: 温度参数，默认0.7
            max_tokens: 最大token数，默认1000
            
        Returns:
            生成的文本
        """
        if model is None:
            model = self.config.default_models.get("text_to_text", "gemini-2.0-flash")
            
        # 构建API URL
        url = f"{self.config.base_url.rstrip('/')}/models/{model}:generateContent?key={self.config.api_key}"
        
        # 构建请求数据
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        # 发送请求
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    
    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> str:
        """
        使用Google进行文本到图像转换，并保存到文件
        
        Args:
            prompt: 输入文本
            model: 模型名称，默认使用配置中的默认模型
            size: 图像尺寸（此参数在Google API中不直接使用）
            quality: 图像质量（此参数在Google API中不直接使用）
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的图像文件路径
        """
        if model is None:
            model = self.config.default_models.get("text_to_image", "gemini-2.0-flash-preview-image-generation")
            
        # 构建API URL
        url = f"{self.config.base_url.rstrip('/')}/models/{model}:generateContent?key={self.config.api_key}"
        
        # 构建请求数据
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"]
            }
        }
        
        # 发送请求
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 提取图像数据
        candidate = result["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            for part in candidate["content"]["parts"]:
                if "inlineData" in part:
                    image_data = part["inlineData"]["data"]
                    mime_type = part["inlineData"]["mimeType"]
                    
                    # 如果没有指定保存路径，则生成默认路径
                    if save_path is None:
                        # 生成文件名
                        hash_object = hashlib.md5(prompt.encode())
                        extension = "png" if "png" in mime_type else "jpg"
                        filename = f"google_{model}_{hash_object.hexdigest()[:8]}.{extension}"
                        
                        # 确保images目录存在
                        images_dir = "images"
                        if not os.path.exists(images_dir):
                            os.makedirs(images_dir)
                            
                        filepath = os.path.join(images_dir, filename)
                    else:
                        filepath = save_path
                        # 确保保存路径的目录存在
                        directory = os.path.dirname(filepath)
                        if directory and not os.path.exists(directory):
                            os.makedirs(directory)
                    
                    # 保存图像
                    with open(filepath, "wb") as f:
                        f.write(base64.b64decode(image_data))
                    
                    return filepath
        
        # 如果没有图像数据，返回文本响应
        if "content" in candidate and "parts" in candidate["content"]:
            text_parts = [part["text"] for part in candidate["content"]["parts"] if "text" in part]
            if text_parts:
                # 如果没有指定保存路径，则生成默认路径
                if save_path is None:
                    # 生成文本文件
                    hash_object = hashlib.md5(prompt.encode())
                    filename = f"google_{model}_{hash_object.hexdigest()[:8]}.txt"
                    
                    # 确保images目录存在
                    images_dir = "images"
                    if not os.path.exists(images_dir):
                        os.makedirs(images_dir)
                        
                    filepath = os.path.join(images_dir, filename)
                else:
                    filepath = save_path
                    # 确保保存路径的目录存在
                    directory = os.path.dirname(filepath)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory)
                
                # 保存文本
                with open(filepath, "w") as f:
                    f.write("\n".join(text_parts))
                
                return filepath
        
        # 默认返回
        raise ValueError("无法生成图像")
