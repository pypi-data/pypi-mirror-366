from __future__ import annotations

from pydantic import BaseModel, Field
import uuid
from typing import List, Optional

from .types import AiModelType, AiModelProvider, AiModelCapability


class ListModelsResponse(BaseModel):
    """Response containing a list of AI models."""
    model_id: str = Field(..., description="Unique identifier for the model")
    model_type: AiModelType = Field(..., description="Type of the AI model")
    provider: AiModelProvider = Field(..., description="Provider of the AI model")
    display_name: Optional[str] = Field(..., description="Human-friendly model name")
    description: Optional[str] = Field(..., description="Model description")
    max_tokens: Optional[int] = Field(..., description="Maximum tokens allowed")
    max_reasoning_tokens: Optional[int] = Field(..., description="Maximum tokens for reasoning")
    capabilities: Optional[List[AiModelCapability]] = Field(..., description="List of model's capabilities")
    use_system_prompt: Optional[bool] = Field(..., description="Should use a system prompt?")
    is_deprecated: Optional[bool] = Field(..., description="Is this model deprecated?")
    is_enabled: Optional[bool] = Field(..., description="Is the model enabled?")
    id: uuid.UUID = Field(..., description="UUID4 for the model record")


class VersionResponse(BaseModel):
    """Response containing API version and run ID."""
    version: str = Field(..., description="API version")
    run_id: str = Field(..., description="Server run/session ID")
    app_version: str = Field(..., description="Application version"
    )

class SimpleChatResponse(BaseModel):
    response: str = Field(..., description="Model's response as a string")
    credits: float = Field(..., description="Number of credits used for the response")
    generation_time: float = Field(..., description="Time taken to generate the response (seconds)"
    )
