from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum
import uuid

from ._utils import id_factory, timestamp_factory


class AiModelCapability(str, Enum):
    CHAT = 'chat'
    STREAM = 'stream'
    REASONING = 'reasoning'
    VISION = 'vision'
    ASSISTANT = 'assistant'
    TOOLS = 'tools'
    RELEVANT_HISTORY = 'relevant_history'
    IMAGE_TO_IMAGE = 'image_to_image'
    IMAGE_UPSCALE = 'image_upscale'
    IMAGE_USE_TRANSLATION = 'image_use_translation'

class AiModelProvider(str, Enum):
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    DEEPSEEK = 'deepseek'
    GOOGLE = 'google'
    XAI = 'xai'
    SD = 'sd'
    BFL = 'bfl'

class AiModelType(str, Enum):
    LLM = 'llm'
    IMG_GEN = 'img_gen'
    STT = 'stt'
    TTS = 'tts'
    EMBEDDINGS = 'embeddings'

class BFLFormat(str, Enum):
    FORMAT_1024_1024 = '1024-1024'
    FORMAT_1440_768 = '1440-768'

class DallEFormat(str, Enum):
    FORMAT_1024X1024 = '1024x1024'
    FORMAT_1792X1024 = '1792x1024'
    FORMAT_1024X1792 = '1024x1792'

class StableDiffusionFormat(str, Enum):
    ONE_TO_ONE = '1:1'
    SIXTEEN_TO_NINE = '16:9'
    NINE_TO_SIXTEEN = '9:16'

class LLMMessageRole(str, Enum):
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'
    TOOL = 'tool'
    INTERNAL = 'internal'


class EncodedData(BaseModel):
    data: str = Field(..., description="Base64-encoded content of the file")
    mime_type: str = Field(..., description="MIME type of the file")
    filename: str = Field("", description="Name of the file")
    size: int = Field("", description="Size of the file in bytes")


    def __init__(self, **data):
        if 'size' not in data or data['size'] is None:
            # Automatically calculate size if not provided
            data['size'] = len(data.get('data', '').encode('utf-8'))
        if 'filename' not in data or data['filename'] is None:
            # Default filename if not provided
            data['filename'] = f"file_{uuid.uuid4()}.bin"
        super().__init__(**data)


class LLMAttachmentData(BaseModel):
    content: str = Field(..., description="Content of the attachment")
    filename: str = Field(..., description="Filename of the attachment")


class LLMB64Image(BaseModel):
    content_type: str = Field(..., description="MIME type of the base64-encoded image")
    b64: str = Field(..., description="Base64-encoded image data")


class LLMVisionData(BaseModel):
    filename: str = Field(..., description="Name of the vision data file")
    size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type for the file")
    file_id: uuid.UUID = Field(..., description="uuid.UUID identifier for the file")
    image_url: str = Field(..., description="URL of the image file")


class ImgGenMessage(BaseModel):
    id: Optional[uuid.UUID] = Field(None, description="uuid.UUID identifier for the message")
    timestamp: Optional[int] = Field(None, description="Unix timestamp of the message")
    model: str = Field(..., description="Model name used for image generation")
    format: Union[DallEFormat, StableDiffusionFormat, BFLFormat] = Field(..., description="Image format returned by the generator")
    hd: Optional[bool] = Field(False, description="Is high-definition output?")
    prompt: str = Field(..., description="Prompt used for image generation")
    content: Optional[str] = Field("", description="Optional additional text content")
    response_id: Optional[str] = Field("", description="ID of the model's response")
    image_url: Optional[str] = Field("", description="URL to the resulting image")
    image_file_id: Optional[uuid.UUID] = Field(None, description="uuid.UUID identifier for the image file")


class LLMMessage(BaseModel):
    id: uuid.UUID = Field(..., default_factory=id_factory, description="uuid.UUID identifier for the message")
    timestamp: int = Field(..., default_factory=timestamp_factory, description="Unix timestamp for the message in milliseconds")
    role: LLMMessageRole = Field(..., description="Role of the message sender")
    content: Optional[str] = Field(None, description="Main text content of the message")
    reasoning_content: Optional[str] = Field(None, description="Optional reasoning explanation")
    model: Optional[str] = Field(None, description="Model name, if specified")
    img_gen: Optional[ImgGenMessage] = Field(None, description="Image generation message, if present")
    vision: Optional[LLMVisionData] = Field(None, description="Vision data for the message, if any")
    documents: Optional[List[LLMAttachmentData]] = Field(None, description="List of attached documents")
    file_ids: List[uuid.UUID] = Field(..., default_factory=list, description="List of uuid.UUID file identifiers")
    file_urls: List[str] = Field(..., default_factory=list, description="List of file URLs")
    b64_images: Optional[List[LLMB64Image]] = Field(None, description="List of base64-encoded images")













