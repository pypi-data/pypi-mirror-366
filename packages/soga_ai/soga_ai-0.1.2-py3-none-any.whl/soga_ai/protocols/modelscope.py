import hashlib
from typing import Optional

import requests
import json

from soga_ai.decorators import register_protocol
from soga_ai.protocols.base import Protocol, ProviderConfig


@register_protocol("modelscope")
class ModelscopeProtocol(Protocol):

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.base_url = config.base_url

    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        ModelScope目前主要支持图像生成，文本到文本功能需要使用其他供应商
        """
        raise NotImplementedError("ModelScope协议目前只支持图像生成功能")

    def text_to_image(self, prompt: str, model: Optional[str] = "MAILAND/majicflus_v1",
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> str:

        """modelscope inference api, see https://www.modelscope.cn/"""
        url = 'https://api-inference.modelscope.cn/v1/images/generations'

        payload = {
            'model': model,  # ModelScope Model-Id,required
            'prompt': prompt
        }

        print(payload)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"ModelScope API调用失败: {response.status_code} - {response.text}")
        
        response_data = response.json()
        
        # 检查响应中是否包含图像URL
        if 'images' not in response_data or not response_data['images']:
            raise Exception(f"ModelScope API响应中未找到图像: {response_data}")
        
        image_url = response_data['images'][0]['url']

        return self.download(image_url, save_path)

    def text_to_audio(self, prompt: str, model: Optional[str] = None,
                      voice: str = "default", speed: float = 1.0,
                      save_path: Optional[str] = None) -> str:
        """
        ModelScope目前主要支持图像生成，文本到音频功能需要使用其他供应商
        """
        raise NotImplementedError("ModelScope协议目前只支持图像生成功能")

