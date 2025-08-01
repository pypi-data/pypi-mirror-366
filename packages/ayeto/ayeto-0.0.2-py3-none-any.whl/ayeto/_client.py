from __future__ import annotations
from ast import List
from typing import Optional
import requests

from pydantic import BaseModel, Field


from ._logger import root_logger
from . import _defaults as defaults
from . import _endpoints as endpoints

from .types import AiModelType, LLMMessage
from .requests import ModelListRequest, SimpleChatRequest, ChatRequest
from .responses import ListModelsResponse, VersionResponse, SimpleChatResponse
from ._exceptions import AyetoException


logger = root_logger.getChild("client")


class AyetoClient(BaseModel):
    base_url: str = Field(defaults.BASE_URL, description="Base URL for the AYETO API")
    api_key: str = Field(defaults.API_KEY, description="API key for authenticating requests to the AYETO API, defaults to environment variable AYETO_API_KEY")

    def list_models(self, model_type: Optional[AiModelType] = None) -> List[ListModelsResponse]:
        """
        Lists available AI models.
        This method retrieves a list of available AI models, optionally filtered by model type.
        Args:
            model_type (Optional[AiModelType]): Filter models by type (e.g., text, image, etc.). 
                                               If None, all models will be returned.
        Returns:
            List[ListModelsResponse]: A list of model information objects.
        Raises:
            AyetoException: If the API request fails or the response cannot be parsed.
        """
        rq = ModelListRequest(model_type=model_type)

        response = self._post_request(endpoints.AI_MODEL_LIST, rq)

        try:
            return [ListModelsResponse.model_validate(item) for item in response.json()]
        except Exception as e:
            raise AyetoException(f"Failed to parse model list response: {e}") from e
        

    def get_version(self) -> VersionResponse:
        """
        Get the Ayeto API version information.
        This method makes an unauthenticated request to the API version endpoint
        and returns the version details as a structured response.
        Returns:
            VersionResponse: An object containing version information about the Ayeto API.
        Raises:
            AyetoException: If there is an error parsing the API response.
        """
        response = self._get_request(endpoints.VERSION, require_auth=False)

        try:
            return VersionResponse.model_validate(response.json())
        except Exception as e:
            raise AyetoException(f"Failed to parse version response: {e}") from e


    def simple_chat(self, model_id: str, prompt: str) -> SimpleChatResponse:
        """
        Send a simple chat request to the AI model.
        This method sends a prompt to the specified AI model and retrieves the response.
        Args:
            model (str): The name of the AI model to use for the chat.
            prompt (str): The text prompt to send to the model.
        Returns:
            SimpleChatResponse: The response from the AI model.
        Raises:
            AyetoException: If the API request fails or the response cannot be parsed.
        """
        rq = SimpleChatRequest(model=model_id, prompt=prompt)

        response = self._post_request(endpoints.CHAT_SIMPLE, rq)

        try:
            return SimpleChatResponse.model_validate(response.json())
        except Exception as e:
            raise AyetoException(f"Failed to parse simple chat response: {e}") from e


    def chat(self, rq: ChatRequest) -> LLMMessage:
        """
        Send a chat request to the AI model.
        This method sends a structured chat request to the specified AI model and retrieves the response.
        Args:
            rq (ChatRequest): The structured request object containing conversation details.
        Returns:
            LLMMessage: The response message from the AI model.
        Raises:
            AyetoException: If the API request fails or the response cannot be parsed.
        """
        if not isinstance(rq, ChatRequest):
            raise AyetoException("Invalid request type. Expected ChatRequest.")
        
        response = self._post_request(endpoints.CHAT, rq)

        try:
            return LLMMessage.model_validate(response.json())
        except Exception as e:
            raise AyetoException(f"Failed to parse chat response: {e}") from e


    def _get_request(self, endpoint: str, params: dict = None, require_auth: bool = True) -> requests.Response:
        """Internal method to perform a GET request to the AYETO API."""

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }

        if require_auth and self.api_key:
            headers["uni-api-key"] = self.api_key

        logger.debug(f"GET {url} with params: {params} and headers: {headers}")
        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            logger.error(f"GET request failed with status {response.status_code}: {response.text}")
            raise AyetoException(f"GET request failed with status {response.status_code}: {response.text}")

        return response

    def _post_request(self, endpoint: str, data: BaseModel, require_auth: bool = True) -> requests.Response:

        """Internal method to perform a POST request to the AYETO API."""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
        }

        if require_auth and self.api_key:
            headers["uni-api-key"] = self.api_key

        logger.debug(f"POST {url} with data: {data} and headers: {headers}")
        response = requests.post(url, json=data.model_dump(mode="json"), headers=headers)

        if response.status_code != 200:
            logger.error(f"POST request failed with status {response.status_code}: {response.text}")
            raise AyetoException(f"POST request failed with status {response.status_code}: {response.text}")

        return response
        
