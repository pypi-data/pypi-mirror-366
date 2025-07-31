import os
from abc import ABC
from io import BytesIO
from pathlib import Path
from typing import List

import requests
from PIL import Image as PILImage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from fastapi import HTTPException
from langchain_core.tools import BaseTool

from saptiva_agents import (SAPTIVA_BASE_URL, DEFAULT_LANG, DEFAULT_TEMPERATURE, MULTIMODAL_MODEL_LIST, DEFAULT_TOP_P,
                            SAPTIVA_API_KEY, SAPTIVA_LEGACY, DEFAULT_THINK, DEFAULT_GUARD, SAPTIVA_MULTIMODAL,
                            SAPTIVA_OPS)
from saptiva_agents import get_messages, get_tools, get_messages_with_image_urls, extract_image_values, \
    get_model_info
from saptiva_agents.agents import AssistantAgent
from saptiva_agents.core import Image, CancellationToken
from saptiva_agents.messages import TextMessage, MultiModalMessage
from saptiva_agents.models.models import AssistantAgentModel, RequestData
from saptiva_agents.tools.langchain import LangChainToolAdapter


class SaptivaAIBase(OpenAIChatCompletionClient):
    """
    Saptiva base class for a model chat completion client
    """
    def __init__(self, **kwargs):
        kwargs.setdefault("lang", DEFAULT_LANG)
        kwargs.setdefault("temperature", DEFAULT_TEMPERATURE)
        kwargs.setdefault("top_p", DEFAULT_TOP_P)

        if not kwargs.get("api_key"):
            raise HTTPException(
                status_code=401,
                detail="El parámetro de cliente api_key debe configurarse ya sea pasando api_key al cliente o "
                       "configurando la variable de entorno SAPTIVA_API_KEY."
            )

        super().__init__(**kwargs)
        self.extra_kwargs = kwargs


class SaptivaAIChatCompletionClient(SaptivaAIBase):
    """
    Saptiva AI Chat Completion Client
    """
    def __init__(self, **kwargs):
        kwargs.setdefault("base_url", SAPTIVA_BASE_URL)
        kwargs.setdefault("api_key", SAPTIVA_API_KEY)
        kwargs.setdefault("model", SAPTIVA_LEGACY)
        kwargs.setdefault("think", DEFAULT_THINK)
        kwargs.setdefault("guard", DEFAULT_GUARD)
        kwargs.setdefault("model_info", get_model_info(model=kwargs.get("model")))
        super().__init__(**kwargs)


class SaptivaAgentsFramework(ABC):
    """
    Saptiva Agents AI Framework
    """
    def __init__(self, data: RequestData):
        self.stream = data.stream
        self.agent_name = data.agent_name
        self.messages = data.messages
        self.model = data.model
        self.tools = data.tools
        self.multimodal = data.multimodal
        self.reflect_on_tool_use = data.reflect_on_tool_use
        self.agent = None
        self.agent_data = None
        self.user_message = None
        self.system_message = None
        self.saptiva_client = None

    async def run(self):
        self.user_message, self.system_message = get_messages(self.messages)
        self.saptiva_client = self._get_saptiva_client()
        self.agent_data = self._get_assistant_agent_model()
        self.agent = self._get_agent()
        return await self._get_agent_response()

    async def run_with_langchain_tools(self):
        self.user_message, self.system_message = get_messages(self.messages)
        self.saptiva_client = self._get_saptiva_client()
        self.agent_data = self._get_assistant_agent_model()
        self.agent = self._get_langchain_base_tool_class_agent()
        return await self._get_agent_response()

    async def run_multimodal(self):
        self.user_message, self.system_message = get_messages_with_image_urls(self.messages)
        self.saptiva_client = self._get_saptiva_multimodal_client()
        self.agent_data = self._get_assistant_agent_model()
        self.agent = self._get_agent()
        image_values = extract_image_values(self.user_message.content)
        return await self._get_agent_response(image_values=image_values)

    def _get_saptiva_multimodal_client(self):
        """
        Determines and returns the appropriate Saptiva client based on the specified model.
        Returns:
            SaptivaAIOllamaClient or SaptivaAIOpenAIClient: the Saptiva client instance.
        """
        self.multimodal = True

        if self.model in MULTIMODAL_MODEL_LIST:
            return self._get_saptiva_client()

        else:
            self.model = SAPTIVA_MULTIMODAL
            return self._get_saptiva_client()

    def _get_saptiva_client(self):
        """
        Determines and returns the appropriate Saptiva client based on the specified model.
        Returns:
            SaptivaAIOllamaClient or SaptivaAIOpenAIClient: the Saptiva client instance.
        """
        if self.multimodal:
            if self.model == SAPTIVA_MULTIMODAL:
                return self._get_saptiva_chat_completion_client(model=SAPTIVA_MULTIMODAL)

            return None

        else:
            if self.model == SAPTIVA_OPS:
                return self._get_saptiva_chat_completion_client(model=SAPTIVA_OPS)

            else:
                # By default, if no specific model is indicated, use Saptiva Legacy.
                return self._get_saptiva_chat_completion_client()

    @staticmethod
    def _get_saptiva_chat_completion_client(model=SAPTIVA_LEGACY):
        """
        Get Saptiva base class for an Ollama model chat completion client
        :param model: (str) Which an Ollama model to use.
        :return: SaptivaAIChatCompletionClient instance
        """
        return SaptivaAIChatCompletionClient(model=model)

    def _get_assistant_agent_model(self):
        """
        Constructs and returns an AssistantAgentModel instance.
        Returns:
            AssistantAgentModel: The constructed agent model.
        """
        try:
            return AssistantAgentModel(
                name=self.agent_name,
                system_message=self.system_message,
                user_message=self.user_message,
                model_client=self.saptiva_client,
                stream=self.stream,
                tools=get_tools(self.tools),
                reflect_on_tool_use=self.reflect_on_tool_use
            )
        except Exception as e:
            raise e

    def _get_agent(self):
        """
        Get Agent with support for function-type tools
        """
        try:
            return AssistantAgent(
                name=self.agent_name,
                system_message=self.system_message.content,
                model_client=self.saptiva_client,
                tools=self.agent_data.tools,
                reflect_on_tool_use=self.reflect_on_tool_use
            )
        except Exception as e:
            raise e

    def _get_langchain_base_tool_class_agent(self):
        """
        Get Agent with support for BaseTool LangChain classes
        """
        try:
            tools = self._validate_if_instance_is_langchain_base_tool(self.agent_data.tools)

            return AssistantAgent(
                name=self.agent_name,
                system_message=self.system_message.content,
                model_client=self.saptiva_client,
                tools=tools,
                reflect_on_tool_use=self.reflect_on_tool_use
            )
        except Exception as e:
            raise e

    def _generate_text_message(self):
        """
        Generates a text message based on the user's content.
        """
        return [TextMessage(
            content=self.user_message.content,
            source=self.user_message.role
        )]

    async def _generate_image_message(self, image_values: List[str]):
        """
        Generates a multimodal message from an image list.
        """
        try:
            images = []

            for value in image_values:
                if value.startswith(('http://', 'https://')):
                    response = requests.get(value)

                    if response.status_code == 200:
                        image_bytes = BytesIO(response.content)
                        img = Image.from_pil(PILImage.open(image_bytes))
                        images.append(img)
                    else:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Error: No se pudo descargar la imágen."
                        )

                elif os.path.exists(value):
                    img = Image.from_file(Path(value))
                    images.append(img)
                else:
                    raise HTTPException(status_code=404, detail="Error: Imágen no encontrada.")

            content = self.user_message.content

            return [MultiModalMessage(
                    content=[content[0]['text'], *images],
                    source=self.user_message.role
            )]

        except Exception as e:
            raise e

    async def _get_agent_response(self, image_values: List[str]=None):
        """
        Get agent response
        """
        try:
            message = await self._generate_image_message(image_values) if image_values else self._generate_text_message()
            response = await self.agent.on_messages(
                messages=message,
                cancellation_token=CancellationToken()
            )

            return response.chat_message.content

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    @staticmethod
    def _validate_if_instance_is_langchain_base_tool(tools):
        """
        Validate if instance is Langchain BaseTool class
        """
        tool_list, aux = [], None
        error = "La herramienta '{tool}' no es compatible con LangChain."

        try:
            for item in tools:
                aux = item
                tool = item()

                if isinstance(tool, BaseTool):
                    tool_list.append(LangChainToolAdapter(tool))
                else:
                    raise HTTPException(status_code=400, detail=error.format(tool=aux.__name__))

            return tool_list

        except TypeError:
            raise HTTPException(status_code=400, detail=error.format(tool=aux.__name__))
