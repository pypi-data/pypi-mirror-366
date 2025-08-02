"""
协议基类定义
"""
import hashlib
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse
import requests


# Content-Type 到文件扩展名的映射
CONTENT_TYPE_MAP = {
    # 图像类型
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'image/svg+xml': '.svg',
    'image/bmp': '.bmp',
    'image/tiff': '.tiff',
    
    # 音频类型
    'audio/mpeg': '.mp3',
    'audio/mp3': '.mp3',
    'audio/wav': '.wav',
    'audio/x-wav': '.wav',
    'audio/ogg': '.ogg',
    'audio/aac': '.aac',
    'audio/flac': '.flac',
    
    # 视频类型
    'video/mp4': '.mp4',
    'video/mpeg': '.mpg',
    'video/quicktime': '.mov',
    'video/x-msvideo': '.avi',
    'video/x-ms-wmv': '.wmv',
    'video/webm': '.webm',
    'video/3gpp': '.3gp',
    'video/ogg': '.ogv',
    
    # 文本类型
    'text/plain': '.txt',
    'text/html': '.html',
    'application/json': '.json',
    'application/xml': '.xml',
    'text/csv': '.csv',
    
    # 二进制文件类型
    'application/pdf': '.pdf',
    'application/zip': '.zip',
    'application/gzip': '.gz',
    'application/x-tar': '.tar',
}

# 扩展名到文件类型的映射
EXTENSION_TYPE_MAP = {
    # 图像类型扩展名
    '.jpg': 'image',
    '.jpeg': 'image',
    '.png': 'image',
    '.gif': 'image',
    '.webp': 'image',
    '.svg': 'image',
    '.bmp': 'image',
    '.tiff': 'image',
    '.tif': 'image',
    
    # 音频类型扩展名
    '.mp3': 'audio',
    '.wav': 'audio',
    '.ogg': 'audio',
    '.aac': 'audio',
    '.flac': 'audio',
    '.m4a': 'audio',
    '.wma': 'audio',
    
    # 视频类型扩展名
    '.mp4': 'video',
    '.mov': 'video',
    '.avi': 'video',
    '.wmv': 'video',
    '.webm': 'video',
    '.mpg': 'video',
    '.mpeg': 'video',
    '.3gp': 'video',
    '.ogv': 'video',
    '.flv': 'video',
    '.mkv': 'video',
}


@dataclass
class ProviderConfig:
    """供应商配置"""
    base_url: str
    api_key: str
    default_models: Dict[str, str] = field(default_factory=dict)
    supported_protocols: List[str] = field(default_factory=list)


class Protocol(ABC):
    """协议基类"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    @abstractmethod
    def text_to_text(self, prompt: str, model: Optional[str] = None,
                     temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        文本到文本转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
        """
        pass
    
    @abstractmethod
    def text_to_image(self, prompt: str, model: Optional[str] = None,
                      size: str = "1024x1024", quality: str = "standard",
                      save_path: Optional[str] = None) -> str:
        """
        文本到图像转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            size: 图像尺寸
            quality: 图像质量
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的图像文件路径
        """
        raise NotImplementedError("此协议未实现文本到图像转换功能")

    @abstractmethod
    def text_to_audio(self, prompt: str, model: Optional[str] = None,
                      voice: str = "default", speed: float = 1.0,
                      save_path: Optional[str] = None) -> str:
        """
        文本到音频转换
        
        Args:
            prompt: 输入文本
            model: 模型名称
            voice: 语音名称
            speed: 语速
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的音频文件路径
        """
        raise NotImplementedError("此协议未实现文本到音频转换功能")

    def download(self, url: str, save_path: Optional[str] = None) -> str:
        """
        下载指定url的内容，如果有save_path，则直接保存，否则输出到output/对应的文件类型/**.扩展名目录下（注意要确保文件的目录存在）
        最后返回保存的路径
        
        Args:
            url: 要下载的文件URL
            save_path: 保存路径，如果不指定则使用默认路径
            
        Returns:
            保存的文件路径
        """
        try:
            # 发送GET请求下载文件
            response = requests.get(url)
            response.raise_for_status()  # 如果响应状态码不是200会抛出异常
            
            # 如果没有指定保存路径，则根据URL和文件类型生成默认路径
            if save_path is None:
                # 解析URL获取文件名
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                # 如果URL中没有文件名，则使用哈希值作为文件名
                if not filename or '.' not in filename:
                    filename = hashlib.md5(url.encode()).hexdigest()[:16]
                
                # 确定文件扩展名
                _, ext = os.path.splitext(filename)
                if not ext:
                    # 尝试从Content-Type推断扩展名
                    content_type = response.headers.get('content-type', '').split(';')[0].strip()
                    ext = CONTENT_TYPE_MAP.get(content_type, '.bin')
                    filename += ext
                
                # 根据文件扩展名确定文件类型目录
                file_type = EXTENSION_TYPE_MAP.get(ext.lower(), 'other')
                
                # 创建output目录结构
                output_dir = os.path.join('output', file_type)
                os.makedirs(output_dir, exist_ok=True)
                
                # 完整保存路径
                save_path = os.path.join(output_dir, filename)
            
            # 确保保存路径的目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存文件
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            return save_path
        except Exception as e:
            raise Exception(f"下载文件失败: {str(e)}")
