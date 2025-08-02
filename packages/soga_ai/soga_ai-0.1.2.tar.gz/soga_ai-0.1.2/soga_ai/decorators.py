"""
装饰器定义，用于注册协议实现
"""

from typing import Dict, Type
from .protocols.base import Protocol

# 存储已注册的协议实现
REGISTERED_PROTOCOLS: Dict[str, Type[Protocol]] = {}


def register_protocol(provider_name: str):
    """
    装饰器，用于注册协议实现
    
    Args:
        provider_name: 供应商名称
    """
    def decorator(cls: Type[Protocol]):
        REGISTERED_PROTOCOLS[provider_name] = cls
        return cls
    return decorator


def get_registered_protocols() -> Dict[str, Type[Protocol]]:
    """
    获取所有已注册的协议实现
    
    Returns:
        已注册的协议实现字典
    """
    return REGISTERED_PROTOCOLS