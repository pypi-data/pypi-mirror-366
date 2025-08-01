import os
from abc import ABCMeta, abstractmethod
from typing import TypeAlias

import aiohttp
import constants
import httpx
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from openai import AsyncOpenAI, DefaultAsyncHttpxClient

ModelProvider: TypeAlias = None | AsyncOpenAI | AsyncAnthropic

load_dotenv()


class OllamaProvider:
    def __init__(self, base_url: str = constants.BASE_LOCAL_OLLAMA):
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key="ollama", base_url=base_url)

    async def get_models(self) -> tuple[str, list[str]]:

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return "Ok", [model["name"] for model in data.get("models", [])]
                    return "No model found in your ollama environment", []
        except Exception as e:
            "Connection error in your ollama environment", []


class LLMStudioProvider:
    def __init__(
        self, api_key: str = "lmstudio", base_url: str = constants.BASE_LOCAL_LMSTUDIO
    ):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def get_models(self) -> tuple[str, list[str]]:
        try:
            models = await self.client.models.list()
            return "Ok", [model.id for model in models.data]
        except Exception as e:
            "Connection error in your lm studio environment", []


class ClientBrand(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.name: str = name
        self.error_messages: list[str] = []

    @abstractmethod
    def get_client(self) -> ModelProvider:
        pass

    def get_error_messages(self):
        return self.error_messages

    def __repr__(self) -> str:
        return self.name


class ClientAnthopicBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientAnthopicBrand")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set ANTHROPIC_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncAnthropic(api_key=api_key)

    def get_client(self) -> ModelProvider:
        return self.client


class ClientCrilBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientCrilBrand")
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set LLM_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(
                base_url=constants.BASE_CRIL_URL,
                api_key=api_key,
                http_client=DefaultAsyncHttpxClient(
                    proxy=None,
                    transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
                ),
            )

    def get_client(self) -> ModelProvider:
        return self.client


class ClientGPTBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientGPTBrand")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set OPENAI_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(api_key=api_key)

    def get_client(self) -> ModelProvider:
        return self.client


class ClientGoogleBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientGoogleBrand")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set GOOGLE_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(
                base_url=constants.BASE_GOOGLE_GEMINI_URL,
                api_key=api_key,
            )

    def get_client(self) -> ModelProvider:
        return self.client


class ClientLocalOllamaBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientLocalOllamaBrand")
        self.client: ModelProvider = AsyncOpenAI(
            base_url=f"{constants.BASE_LOCAL_OLLAMA}/v1", api_key="no needed"
        )

    def get_client(self) -> ModelProvider:
        return self.client


class ClientLocalLmstudioBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientLocalLmstudioBrand")
        self.client: ModelProvider = AsyncOpenAI(
            base_url=constants.BASE_LOCAL_LMSTUDIO, api_key="no needed"
        )

    def get_client(self) -> ModelProvider:
        return self.client
