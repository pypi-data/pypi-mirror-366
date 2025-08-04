"""
单元测试
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from soga_ai import Client, ProviderConfig


def test_client_initialization():
    """测试客户端初始化"""
    # 保存原始环境变量
    original_openai_key = os.environ.get("OPENAI_API_KEY")
    original_google_key = os.environ.get("GOOGLE_API_KEY")
    
    # 清除环境变量以进行测试
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "GOOGLE_API_KEY" in os.environ:
        del os.environ["GOOGLE_API_KEY"]
    
    try:
        # 测试不带API密钥的初始化
        client = Client()
        assert client is not None
        # 现在应该有三个供应商：openai, google, ollama
        assert len(client.config_manager.get_provider_names()) >= 3
        
        # 测试带API密钥的初始化
        client_with_keys = Client("test-openai-key", "test-google-key")
        openai_config = client_with_keys.config_manager.get_provider("openai")
        google_config = client_with_keys.config_manager.get_provider("google")
        assert openai_config.api_key == "test-openai-key"
        assert google_config.api_key == "test-google-key"
    finally:
        # 恢复原始环境变量
        if original_openai_key:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        if original_google_key:
            os.environ["GOOGLE_API_KEY"] = original_google_key


@patch('openai.OpenAI')
def test_text_to_text_default(mock_openai):
    """测试默认文本到文本转换"""
    # 模拟OpenAI客户端和响应
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Bonjour, comment allez-vous?"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client
    
    client = Client()
    result = client.text_to_text("Translate to French: 'Hello, how are you?'")
    
    # 验证结果
    assert result == "Bonjour, comment allez-vous?"
    
    # 验证OpenAI客户端被正确调用
    mock_client.chat.completions.create.assert_called_once()


@patch('openai.OpenAI')
@patch('requests.get')
def test_text_to_image_default(mock_requests_get, mock_openai):
    """测试默认文本到图像转换"""
    # 模拟OpenAI客户端和响应
    mock_response = MagicMock()
    mock_response.data[0].url = "https://example.com/generated_image.png"
    mock_client = MagicMock()
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # 模拟requests.get响应
    mock_image_response = MagicMock()
    mock_image_response.content = b"fake image data"
    mock_requests_get.return_value = mock_image_response
    
    client = Client()
    result = client.text_to_image("A beautiful sunset")
    
    # 验证结果是文件路径
    assert result.startswith("images/openai_")
    assert result.endswith(".png")
    
    # 验证文件是否存在
    assert os.path.exists(result)
    
    # 清理测试文件
    if os.path.exists(result):
        os.remove(result)
    
    # 验证OpenAI客户端被正确调用
    mock_client.images.generate.assert_called_once()


@patch('requests.post')
def test_text_to_text_with_provider(mock_post):
    """测试指定供应商的文本到文本转换"""
    # 模拟Google API响应
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "Hello, world!"
                }]
            }
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client = Client()
    result = client.text_to_text("Hello, world!", provider="google")
    
    # 验证结果
    assert result == "Hello, world!"
    
    # 验证requests.post被正确调用
    mock_post.assert_called_once()


@patch('requests.post')
def test_text_to_image_with_provider(mock_post):
    """测试指定供应商的文本到图像转换"""
    # 模拟Google API响应
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{
                    "inlineData": {
                        "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        "mimeType": "image/png"
                    }
                }]
            }
        }]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client = Client()
    result = client.text_to_image("A beautiful sunset", provider="google")
    
    # 验证结果是文件路径
    assert result.startswith("images/google_")
    assert result.endswith(".png")
    
    # 验证文件是否存在
    assert os.path.exists(result)
    
    # 清理测试文件
    if os.path.exists(result):
        os.remove(result)
    
    # 验证requests.post被正确调用
    mock_post.assert_called_once()


def test_add_custom_provider():
    """测试添加自定义供应商"""
    client = Client()
    custom_config = ProviderConfig(
        base_url="https://custom.example.com",
        api_key="custom-key",
        default_models={"text_to_text": "custom-model"},
        supported_protocols=["text_to_text"]
    )
    client.add_provider("custom", custom_config, "openai")  # 指定使用OpenAI协议实现
    assert "custom" in client.config_manager.get_provider_names()
    
    # 验证协议映射是否正确
    protocol_impl = client.config_manager.get_provider_protocol_impl("custom")
    assert protocol_impl == "openai"


def test_set_api_key():
    """测试设置API密钥"""
    # 保存原始环境变量
    original_openai_key = os.environ.get("OPENAI_API_KEY")
    
    # 清除环境变量以进行测试
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    
    try:
        client = Client()
        
        # 更新API密钥
        client.set_api_key("openai", "new-openai-key")
        
        # 验证API密钥已更新
        openai_config = client.config_manager.get_provider("openai")
        assert openai_config.api_key == "new-openai-key"
    finally:
        # 恢复原始环境变量
        if original_openai_key:
            os.environ["OPENAI_API_KEY"] = original_openai_key


@patch('openai.OpenAI')
@patch('requests.get')
def test_custom_parameters(mock_requests_get, mock_openai):
    """测试自定义参数"""
    # 模拟OpenAI客户端和响应
    mock_response = MagicMock()
    mock_response.data[0].url = "https://example.com/generated_image.png"
    mock_client = MagicMock()
    mock_client.images.generate.return_value = mock_response
    mock_openai.return_value = mock_client
    
    # 模拟requests.get响应
    mock_image_response = MagicMock()
    mock_image_response.content = b"fake image data"
    mock_requests_get.return_value = mock_image_response
    
    client = Client()
    result = client.text_to_image("A beautiful sunset", model="custom-model")
    
    # 验证结果是文件路径
    assert result.startswith("images/openai_")
    assert "custom-model" in result
    assert result.endswith(".png")
    
    # 验证文件是否存在
    assert os.path.exists(result)
    
    # 清理测试文件
    if os.path.exists(result):
        os.remove(result)
    
    # 验证OpenAI客户端被正确调用
    mock_client.images.generate.assert_called_once()


def test_ollama_provider_config():
    """测试Ollama供应商配置"""
    client = Client()
    ollama_config = client.config_manager.get_provider("ollama")
    assert ollama_config is not None
    assert ollama_config.base_url == "http://localhost:11434/v1"
    assert ollama_config.default_models["text_to_text"] == "gemma3:1b"
    
    # 检查Ollama是否正确映射到OpenAI协议实现
    protocol_impl = client.config_manager.get_provider_protocol_impl("ollama")
    assert protocol_impl == "openai"


def test_ollama_text_to_text():
    """测试Ollama文本到文本转换（需要本地Ollama服务）"""
    client = Client()
    result = client.text_to_text("Say 'Hello, World!' in English", provider="ollama")
    assert isinstance(result, str)
    assert len(result) > 0