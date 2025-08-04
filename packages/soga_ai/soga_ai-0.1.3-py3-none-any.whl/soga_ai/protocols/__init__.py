"""
协议模块初始化文件
"""

# 确保协议实现被导入和注册
from . import openai
from . import google
from . import edge
from . import modelscope

# Ollama使用OpenAI协议实现，因此不需要单独的实现文件
# 我们只需要确保OpenAI协议实现被正确导入即可

__all__ = ["openai", "google", "edge", "modelscope"]