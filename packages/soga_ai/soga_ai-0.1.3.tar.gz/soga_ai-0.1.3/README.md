# soga_ai

soga_ai是一个封装了大模型相关接口的Python库，提供了统一的API来调用不同的AI供应商（如OpenAI、Google等）的服务。

## 特性

- 统一的API接口，简化AI模型调用
- 支持多种AI供应商（OpenAI、Google、Ollama、ModelScope等）
- 可扩展的架构，易于添加新的供应商和协议
- 强类型支持，提高代码健壮性
- 灵活的供应商配置，支持动态添加供应商
- 支持文本生成、图像生成和音频生成功能
- 图像和音频自动生成并保存到文件
- 简化的API密钥配置方式
- 支持自定义保存路径
- 支持文件下载功能

## 安装

```bash
pip install soga_ai
```

## 快速开始

首先设置环境变量：

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export MODELSCOPE_API_KEY="your-modelscope-api-key"
```

然后在代码中使用：

```python
from soga_ai import Client

# 创建客户端实例（API密钥从环境变量自动读取）
client = Client()

# 或者直接在代码中提供API密钥
# client = Client(
#     openai_api_key="your-openai-api-key",
#     google_api_key="your-google-api-key"
# )

# 使用默认供应商进行文本到文本转换
result = client.text_to_text("Translate the following English text to French: 'Hello, how are you?'")
print(result)

# 使用默认供应商进行文本到图像转换（图像会自动保存到文件）
image_path = client.text_to_image("A beautiful sunset over the ocean")
print(f"Image saved to: {image_path}")

# 使用默认供应商进行文本到音频转换（音频会自动保存到文件）
audio_path = client.text_to_audio("你好，这是一个文本转语音的示例。")
print(f"Audio saved to: {audio_path}")

# 指定特定供应商调用
result = client.text_to_text("Summarize this article", provider="google")

# 使用Ollama本地模型
result = client.text_to_text("Explain quantum computing in simple terms", provider="ollama")

# 使用ModelScope图像生成
image_path = client.text_to_image("A beautiful sunset over the ocean", provider="modelscope")

# 使用自定义参数调用
result = client.text_to_text(
    "Write a short poem about technology",
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.5,
    max_tokens=500
)

# 使用自定义保存路径
image_path = client.text_to_image(
    "A beautiful sunset over the ocean", 
    save_path="my_images/sunset.png"
)
print(f"Image saved to: {image_path}")

audio_path = client.text_to_audio(
    "你好，这是一个文本转语音的示例。",
    save_path="my_audio/example.mp3"
)
print(f"Audio saved to: {audio_path}")

# 下载文件
download_path = client.download("https://example.com/file.jpg")
print(f"File downloaded to: {download_path}")

# 下载文件到自定义路径
download_path = client.download("https://example.com/file.jpg", "my_downloads/file.jpg")
print(f"File downloaded to: {download_path}")
```

## 使用Google图像生成

soga_ai支持使用Google的原生图像生成功能，生成的图像会自动保存到文件：

```python
from soga_ai import Client

client = Client()

# 生成图像（自动保存到文件）
image_path = client.text_to_image(
    "A beautiful sunset over a futuristic city with flying cars",
    provider="google"
)

print(f"Image saved to: {image_path}")

# 使用自定义保存路径
image_path = client.text_to_image(
    "A beautiful sunset over a futuristic city with flying cars",
    provider="google",
    save_path="custom_images/google_sunset.png"
)

print(f"Image saved to: {image_path}")
```

## 使用ModelScope图像生成

soga_ai支持使用ModelScope的图像生成功能，生成的图像会自动保存到文件：

```python
from soga_ai import Client

client = Client()

# 生成图像（自动保存到文件）
image_path = client.text_to_image(
    "A beautiful sunset over a futuristic city with flying cars",
    provider="modelscope"
)

print(f"Image saved to: {image_path}")

# 使用自定义保存路径
image_path = client.text_to_image(
    "A beautiful sunset over a futuristic city with flying cars",
    provider="modelscope",
    save_path="custom_images/modelscope_sunset.png"
)

print(f"Image saved to: {image_path}")
```

## 使用Edge文本到音频

soga_ai支持使用Microsoft Edge的文本到语音功能（通过edge-tts库），生成的音频会自动保存到文件：

```python
from soga_ai import Client

client = Client()

# 生成音频（自动保存到文件）
audio_path = client.text_to_audio(
    "你好，这是一个文本转语音的示例。",
    provider="edge"
)

print(f"Audio saved to: {audio_path}")

# 使用自定义参数
audio_path = client.text_to_audio(
    "This is a text to speech example with custom parameters.",
    provider="edge",
    model="en-US-JennyNeural",
    speed=1.25  # 1.25倍速
)

print(f"Audio saved to: {audio_path}")

# 使用自定义保存路径
audio_path = client.text_to_audio(
    "This is a text to speech example with a custom save path.",
    provider="edge",
    save_path="custom_audio/example.mp3"
)

print(f"Audio saved to: {audio_path}")
```

## 使用Ollama

要使用Ollama本地模型，需要先安装Ollama并拉取模型：

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取gemma3模型
ollama run gemma3:1b
```

Ollama默认在`http://localhost:11434`运行，soga_ai已经配置好通过OpenAI兼容API与Ollama通信。

## 动态添加供应商

soga_ai支持动态添加新的供应商：

```python
from soga_ai import Client, ProviderConfig

client = Client()

# 添加自定义供应商配置
custom_config = ProviderConfig(
    base_url="https://custom-api.example.com/v1",
    api_key="your-custom-key",
    default_models={
        "text_to_text": "custom-model-v1",
        "text_to_image": "custom-image-model-v1"
    },
    supported_protocols=["text_to_text", "text_to_image"]
)

# 添加供应商并指定使用的协议实现
client.add_provider("custom", custom_config, "openai")  # 使用OpenAI协议实现
```

## 开发

### 安装依赖

```bash
uv sync
```

### 运行测试

```bash
uv run pytest tests/
```

### 运行示例

```bash
# 运行基本使用示例
export OPENAI_API_KEY="your-openai-api-key"
export GOOGLE_API_KEY="your-google-api-key"
uv run python examples/basic_usage.py

# 运行Google图像生成示例
export GOOGLE_API_KEY="your-google-api-key"
uv run python examples/google_image_generation.py

# 运行ModelScope图像生成示例
export MODELSCOPE_API_KEY="your-modelscope-api-key"
uv run python examples/modelscope_image_generation.py

# 运行Edge文本到音频示例
uv run python examples/edge_text_to_audio.py

# 运行动态添加供应商示例
uv run python examples/dynamic_provider.py

# 运行自定义保存路径示例
uv run python examples/custom_save_path_image.py
uv run python examples/custom_save_path_audio.py

# 运行下载功能示例
uv run python examples/download_example.py
```