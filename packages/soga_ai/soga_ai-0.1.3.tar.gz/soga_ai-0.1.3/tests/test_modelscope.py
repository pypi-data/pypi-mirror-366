import unittest
import sys
import os

# Add the soga_ai directory to the path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from soga_ai.client import Client
from soga_ai.decorators import get_registered_protocols


class TestModelScopeProtocol(unittest.TestCase):
    def test_modelscope_protocol_registration(self):
        """测试ModelScope协议是否正确注册"""
        # 获取所有已注册的协议
        protocols = get_registered_protocols()
        
        # 检查ModelScope协议是否已注册
        self.assertIn("modelscope", protocols)
        self.assertIsNotNone(protocols["modelscope"])
        
    def test_client_initialization(self):
        """测试客户端初始化时是否包含ModelScope供应商"""
        client = Client()
        
        # 检查ModelScope供应商是否在配置管理器中
        provider_names = client.config_manager.get_provider_names()
        self.assertIn("modelscope", provider_names)
        
    def test_modelscope_protocol_methods(self):
        """测试ModelScope协议是否实现了所有必需的方法"""
        from soga_ai.protocols.modelscope import ModelscopeProtocol
        from soga_ai.protocols.base import ProviderConfig
        
        # 创建一个测试配置
        config = ProviderConfig(
            base_url="",
            api_key="test-key",
            default_models={"text_to_image": "test-model"},
            supported_protocols=["text_to_image"]
        )
        
        # 实例化协议
        protocol = ModelscopeProtocol(config)
        
        # 检查是否实现了所有必需的方法
        self.assertTrue(hasattr(protocol, 'text_to_text'))
        self.assertTrue(hasattr(protocol, 'text_to_image'))
        self.assertTrue(hasattr(protocol, 'text_to_audio'))
        self.assertTrue(hasattr(protocol, 'download'))


if __name__ == '__main__':
    unittest.main()