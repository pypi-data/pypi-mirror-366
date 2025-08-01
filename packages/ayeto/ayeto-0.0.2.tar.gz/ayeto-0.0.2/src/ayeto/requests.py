from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional
import uuid
from typing import List

from . import _defaults as defaults
from .types import AiModelType, LLMMessage, EncodedData


class ModelListRequest(BaseModel):
    """Request to list AI models with optional filtering."""
    model_type: Optional[AiModelType] = Field(None, description="Type of AI model to filter the request (optional)")


class SimpleChatRequest(BaseModel):
    """Request for a simple chat interaction with an AI model."""
    model: str = Field(..., description="LLM model to use")
    prompt: str = Field(..., description="Prompt text for the model")


class ChatRequest(BaseModel):
    """Request for a chat interaction with an AI model."""
    conversation_id: uuid.UUID = Field(..., default_factory=uuid.uuid4, description="uuid.UUID identifier of the conversation")
    assistant_id: Optional[uuid.UUID] = Field(None, description="uuid.UUID identifier of the assistant")
    message: LLMMessage = Field(..., description="Message content from the user")
    model: str = Field(..., description="LLM model name to use")
    img_gen_model: Optional[str] = Field(defaults.IMG_GEN_MODEL, description="Image generation model name")
    image: Optional[bool] = Field(False, description="Flag to indicate if image features are used")
    vision: Optional[EncodedData] = Field(None, description="Vision payload for the request")
    documents: Optional[List[EncodedData]] = Field(None, description="Attached documents for the conversation")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens in the response")
    relevant_history: Optional[bool] = Field(True, description="Whether to include relevant conversation history")
    dynamic_tools: Optional[bool] = Field(True, description="Use dynamic tool integration")