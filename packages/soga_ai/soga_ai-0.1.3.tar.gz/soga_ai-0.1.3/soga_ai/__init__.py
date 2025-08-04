"""
soga_ai主模块
"""

# 确保协议实现被正确导入和注册
from . import protocols

from .client import Client
from .protocols.base import ProviderConfig

__all__ = ["Client", "ProviderConfig"]