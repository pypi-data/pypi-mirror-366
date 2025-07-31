from typing import List, Any, Callable, Awaitable

from autogen_core.tools import BaseTool
from pydantic import BaseModel, Field

class Message(BaseModel):
    content: str | List[dict]
    role: str
    name: str = None


class RequestData(BaseModel):
    stream: bool = Field(default=False, description="Response message in tokens format.")
    agent_name: str = Field(default="assistant", description="Role of the agent.")
    messages: List[Message] = Field(..., description="Messages from the user.")
    model: str = Field(default="saptiva turbo", description="Model client to use.")
    tools: List[str] = Field(default=[], description="Tools to use.")
    multimodal: bool = Field(default=False, description="Enable if the model support multimodal input.")
    reflect_on_tool_use: bool = Field(
        default=True,
        description="Set to True to have the model reflect on the tool use, set to False to return the "
                    "tool call result directly.")


class AssistantAgentModel(BaseModel):
    name: str = Field(default="assistant", description="Role of the agent.")
    system_message: Message = Field(description="System message of the agent.")
    user_message: Message = Field(..., description="User message for the agent.")
    model_client: Any = Field(..., description="Model client to use.")
    stream: bool = Field(default=False, description="Response message in tokens format.")
    tools: List[BaseTool[Any, Any] | Callable[..., Any] | Callable[..., Awaitable[Any]]] | None = Field(
        default=[], description="Tools to use.")
    reflect_on_tool_use: bool = Field(
        default=True,
        description="Set to True to have the model reflect on the tool use, set to False to return the tool call result"
                    " directly.")

    model_config = {
        "arbitrary_types_allowed": True
    }