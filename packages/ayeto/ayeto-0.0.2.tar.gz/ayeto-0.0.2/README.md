# AYETO API Client

A Python client library for interacting with the AYETO.ai API. This library provides a simple and intuitive interface to access various AI models for chat, image generation, and other AI capabilities.

## Features

- 🤖 **Multiple AI Models**: Support for various AI providers (OpenAI, Anthropic, DeepSeek, Google, XAI, and more)
- 💬 **Chat Functionality**: Simple and advanced chat interactions with AI models
- 🖼️ **Image Generation**: Support for image generation models (DALL-E, Stable Diffusion, BFL)
- 📁 **Document Support**: Upload and process documents in conversations
- 👁️ **Vision Capabilities**: Process images with vision-enabled models
- 🔧 **Tool Integration**: Dynamic tool integration for enhanced AI capabilities
- 📝 **Type Safety**: Full type hints and Pydantic models for request/response validation

## Installation

```bash
pip install ayeto
```

## Quick Start

### Setting up the Client

```python
from ayeto import AyetoClient

# Initialize with API key from environment variable AYETO_API_KEY
client = AyetoClient()

# Or provide API key directly
client = AyetoClient(api_key="your-api-key-here")

# Custom base URL (optional)
client = AyetoClient(
    api_key="your-api-key-here",
    base_url="https://custom-ayeto-instance.com/api/v2"
)
```

### Getting Your API Key

To use this client, you'll need an API key from your AYETO account:

1. Sign up or log in at [https://ayeto.ai](https://ayeto.ai)
2. Go to your profile settings
3. Generate or copy your API key

### Environment Variables

Set your API key as an environment variable:

```bash
export AYETO_API_KEY="your-api-key-here"
```

## Usage Examples

### List Available Models

```python
# List all available models
models = client.list_models()
for model in models:
    print(f"Model ID: {model.model_id}, Name: {model.display_name}, Type: {model.model_type}")

# Filter by model type
llm_models = client.list_models(model_type="llm")
image_models = client.list_models(model_type="img_gen")
```

### Simple Chat

```python
# Simple chat interaction
response = client.simple_chat(
    model_id="gpt-4.1-mini",
    prompt="What is the capital of France?"
)
print(response.message)
```

### Advanced Chat

```python
from ayeto.types import LLMMessage
from ayeto.requests import ChatRequest

# Create a message
message = LLMMessage(
    role="user",
    content="Explain quantum computing in simple terms"
)

# Create chat request
chat_request = ChatRequest(
    model="gpt-4.1",
    message=message,
    max_tokens=500,
    relevant_history=True,
    dynamic_tools=True
)

# Send chat request
response = client.chat(chat_request)
print(response.content)
```

### Chat with Images (Vision)

```python
from ayeto.types import LLMMessage, EncodedData
from ayeto.requests import ChatRequest

# Encode your image (base64 encoded data)
vision_data = EncodedData(
    data="base64-encoded-image-data",
    mime_type="image/jpeg"
)

message = LLMMessage(
    role="user", 
    content="What do you see in this image?"
)

chat_request = ChatRequest(
    model="gpt-4.1",
    message=message,
    vision=vision_data
)

response = client.chat(chat_request)
```

### Chat with Document Upload

```python
from ayeto.types import EncodedData

# Encode your document
document = EncodedData(
    data="base64-encoded-document-data",
    mime_type="application/pdf"
)

chat_request = ChatRequest(
    model="gpt-4.1-mini",
    message=message,
    documents=[document]
)

response = client.chat(chat_request)
```

### Get API Version

```python
version_info = client.get_version()
print(f"API Version: {version_info.version}")
```

## API Reference

### AyetoClient

The main client class for interacting with the AYETO API.

#### Methods

- `list_models(model_type: Optional[AiModelType] = None) -> List[ListModelsResponse]`
  - List available AI models, optionally filtered by type
  
- `simple_chat(model_id: str, prompt: str) -> SimpleChatResponse`
  - Send a simple chat request to an AI model
  
- `chat(request: ChatRequest) -> LLMMessage`
  - Send an advanced chat request with full feature support
  
- `get_version() -> VersionResponse`
  - Get API version information

### Model Types

- `LLM`: Large Language Models for text generation and chat
- `IMG_GEN`: Image generation models
- `STT`: Speech-to-text models  
- `TTS`: Text-to-speech models
- `EMBEDDINGS`: Text embedding models

### Supported Providers

- **OpenAI**: GPT models, DALL-E
- **Anthropic**: Claude models
- **DeepSeek**: DeepSeek models
- **Google**: Gemini models
- **XAI**: Grok models
- **SD**: Stable Diffusion models
- **BFL**: Black Forest Labs models

## Error Handling

The library raises `AyetoException` for API-related errors:

```python
from ayeto.exceptions import AyetoException

try:
    response = client.simple_chat("invalid-model", "Hello")
except AyetoException as e:
    print(f"API Error: {e}")
```

## Requirements

- Python 3.12.3+
- requests
- pydantic

## License

This project is licensed under the terms specified in the LICENSE file.

## Changelog

### v0.0.2
- Project urls added

### v0.0.1
- Initial release
- Basic chat functionality
- Model listing
- Support for multiple AI providers
- Vision and document capabilities