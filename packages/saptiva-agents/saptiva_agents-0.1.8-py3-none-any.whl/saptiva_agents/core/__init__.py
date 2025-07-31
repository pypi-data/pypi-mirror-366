from autogen_core import message_handler, default_subscription, type_subscription, Component, FunctionCall, ClosureAgent

from saptiva_agents.core._agent_id import AgentId
from saptiva_agents.core._closure_agent import ClosureContext
from saptiva_agents.core._core import Image, CancellationToken, BufferedChatCompletionContext, \
    UnboundedChatCompletionContext
from saptiva_agents.core._default_topic import DefaultTopicId
from saptiva_agents.core._message_context import MessageContext
from saptiva_agents.core._routed_agent import RoutedAgent
from saptiva_agents.core._single_threaded_agent_runtime import SingleThreadedAgentRuntime
from saptiva_agents.core._topic import TopicId
from saptiva_agents.core._type_subscription import TypeSubscription
from saptiva_agents import (
    EVENT_LOGGER_NAME as EVENT_LOGGER_NAME_ALIAS,
)
from saptiva_agents import (
    ROOT_LOGGER_NAME as ROOT_LOGGER_NAME_ALIAS,
)
from saptiva_agents import (
    TRACE_LOGGER_NAME as TRACE_LOGGER_NAME_ALIAS,
)
from saptiva_agents import (
    JSON_DATA_CONTENT_TYPE as JSON_DATA_CONTENT_TYPE_ALIAS,
)
from saptiva_agents import (
    PROTOBUF_DATA_CONTENT_TYPE as PROTOBUF_DATA_CONTENT_TYPE_ALIAS,
)

EVENT_LOGGER_NAME = EVENT_LOGGER_NAME_ALIAS
"""The name of the logger used for structured events."""

ROOT_LOGGER_NAME = ROOT_LOGGER_NAME_ALIAS
"""The name of the root logger."""

TRACE_LOGGER_NAME = TRACE_LOGGER_NAME_ALIAS
"""Logger name used for developer intended trace logging. The content and format of this log should not be depended upon."""

JSON_DATA_CONTENT_TYPE = JSON_DATA_CONTENT_TYPE_ALIAS
"""The content type for JSON data."""

PROTOBUF_DATA_CONTENT_TYPE = PROTOBUF_DATA_CONTENT_TYPE_ALIAS
"""The content type for Protobuf data."""


__all__ = [
    "Image",
    "CancellationToken",
    "BufferedChatCompletionContext",
    "UnboundedChatCompletionContext",
    "Component",
    "SingleThreadedAgentRuntime",
    "message_handler",
    "type_subscription",
    "RoutedAgent",
    "MessageContext",
    "AgentId",
    "TopicId",
    "TypeSubscription",
    "DefaultTopicId",
    "default_subscription",
    "ClosureContext",
    "ClosureAgent",
    "FunctionCall",
    "EVENT_LOGGER_NAME",
    "ROOT_LOGGER_NAME",
    "TRACE_LOGGER_NAME",
    "JSON_DATA_CONTENT_TYPE",
    "PROTOBUF_DATA_CONTENT_TYPE"
]

