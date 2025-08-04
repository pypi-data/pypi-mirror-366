import os
import tempfile
import unittest
from unittest.mock import patch, Mock
import sys
import hashlib
from urllib.parse import urlparse

# Add the soga_ai directory to the path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from soga_ai.protocols.base import Protocol, ProviderConfig


class MockProtocol(Protocol):
    """用于测试的模拟协议类"""
    def text_to_text(self, prompt: str, model=None, temperature=0.7, max_tokens=1000):
        pass

    def text_to_image(self, prompt: str, model=None, size="1024x1024", quality="standard", save_path=None):
        pass

    def text_to_audio(self, prompt: str, model=None, voice="default", speed=1.0, save_path=None):
        pass


class TestDownloadFunction(unittest.TestCase):
    def setUp(self):
        config = ProviderConfig(base_url="https://api.example.com", api_key="test-key")
        self.protocol = MockProtocol(config)
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # 清理临时文件和目录
        if os.path.exists(self.temp_dir):
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)
    
    @patch('soga_ai.protocols.base.requests.get')
    def test_download_with_custom_path(self, mock_get):
        # 模拟HTTP响应
        mock_response = Mock()
        mock_response.content = b"test content"
        mock_response.headers = {}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试自定义保存路径
        test_path = os.path.join(self.temp_dir, "test_file.txt")
        result_path = self.protocol.download("https://example.com/test.txt", test_path)
        
        # 验证结果
        self.assertEqual(result_path, test_path)
        mock_get.assert_called_once_with("https://example.com/test.txt")
        
        # 验证文件内容
        with open(result_path, 'rb') as f:
            self.assertEqual(f.read(), b"test content")
    
    @patch('soga_ai.protocols.base.requests.get')
    def test_download_with_default_path_image(self, mock_get):
        # 模拟图片HTTP响应
        mock_response = Mock()
        mock_response.content = b"image content"
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试默认保存路径（图片）
        result_path = self.protocol.download("https://example.com/test_image")
        
        # 验证结果
        self.assertTrue(result_path.startswith("output/image/"))
        self.assertTrue(result_path.endswith(".jpg"))
        mock_get.assert_called_once_with("https://example.com/test_image")
    
    @patch('soga_ai.protocols.base.requests.get')
    def test_download_with_default_path_audio(self, mock_get):
        # 模拟音频HTTP响应
        mock_response = Mock()
        mock_response.content = b"audio content"
        mock_response.headers = {'content-type': 'audio/mpeg'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试默认保存路径（音频）
        result_path = self.protocol.download("https://example.com/test_audio")
        
        # 验证结果
        self.assertTrue(result_path.startswith("output/audio/"))
        self.assertTrue(result_path.endswith(".mp3"))
        mock_get.assert_called_once_with("https://example.com/test_audio")
    
    @patch('soga_ai.protocols.base.requests.get')
    def test_download_with_default_path_video(self, mock_get):
        # 模拟视频HTTP响应
        mock_response = Mock()
        mock_response.content = b"video content"
        mock_response.headers = {'content-type': 'video/mp4'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试默认保存路径（视频）
        result_path = self.protocol.download("https://example.com/test_video")
        
        # 验证结果
        self.assertTrue(result_path.startswith("output/video/"))
        self.assertTrue(result_path.endswith(".mp4"))
        mock_get.assert_called_once_with("https://example.com/test_video")
    
    @patch('soga_ai.protocols.base.requests.get')
    def test_download_with_default_path_unknown(self, mock_get):
        # 模拟未知类型HTTP响应
        mock_response = Mock()
        mock_response.content = b"unknown content"
        mock_response.headers = {'content-type': 'application/octet-stream'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # 测试默认保存路径（未知类型）
        result_path = self.protocol.download("https://example.com/test_unknown")
        
        # 验证结果
        self.assertTrue(result_path.startswith("output/other/"))
        self.assertTrue(result_path.endswith(".bin"))
        mock_get.assert_called_once_with("https://example.com/test_unknown")


if __name__ == '__main__':
    unittest.main()