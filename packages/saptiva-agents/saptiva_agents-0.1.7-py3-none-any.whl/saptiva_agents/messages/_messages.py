from autogen_agentchat.messages import TextMessage, MultiModalMessage, StopMessage, HandoffMessage, \
    ToolCallRequestEvent, ToolCallExecutionEvent, ToolCallSummaryMessage, UserInputRequestedEvent, MemoryQueryEvent, \
    ModelClientStreamingChunkEvent, ThoughtEvent, StructuredMessage, BaseMessage, BaseChatMessage, BaseTextChatMessage, \
    BaseAgentEvent


class BaseMessage(BaseMessage):
    """Abstract base class for all message types in Saptiva-Agents.

    .. warning::

        If you want to create a new message type, do not inherit from this class.
        Instead, inherit from :class:`BaseChatMessage` or :class:`BaseAgentEvent`
        to clarify the purpose of the message type.

    """
    pass


class BaseChatMessage(BaseChatMessage):
    """Abstract base class for chat messages.

    .. note::

        If you want to create a new message type that is used for agent-to-agent
        communication, inherit from this class, or simply use
        :class:`StructuredMessage` if your content type is a subclass of
        Pydantic BaseModel.

    This class is used for messages that are sent between agents in a chat
    conversation. Agents are expected to process the content of the
    message using models and return a response as another :class:`BaseChatMessage`.
    """
    content: str
    """The content of the message."""


class BaseTextChatMessage(BaseTextChatMessage):
    """Base class for all text-only :class:`BaseChatMessage` types.
    It has implementations for :meth:`to_text`, :meth:`to_model_text`,
    and :meth:`to_model_message` methods.

    Inherit from this class if your message content type is a string.
    """
    pass


class BaseAgentEvent(BaseAgentEvent):
    """Base class for agent events.

    .. note::

        If you want to create a new message type for signaling observable events
        to user and application, inherit from this class.

    Agent events are used to signal actions and thoughts produced by agents
    and teams to user and applications. They are not used for agent-to-agent
    communication and are not expected to be processed by other agents.

    You should override the :meth:`to_text` method if you want to provide
    a custom rendering of the content.
    """
    pass


class StructuredMessage(StructuredMessage):
    """A :class:`BaseChatMessage` type with an unspecified content type.

        To create a new structured message type, specify the content type
        as a subclass of `Pydantic BaseModel <https://docs.pydantic.dev/latest/concepts/models/>`_.

        .. code-block:: python

            from pydantic import BaseModel
            from saptiva_agents.messages import StructuredMessage

            class MyMessageContent(BaseModel):
                text: str
                number: int

            message = StructuredMessage[MyMessageContent](
                content=MyMessageContent(text="Hello", number=42),
                source="agent1"
            )

            print(message.to_text())  # {"text": "Hello", "number": 42}
        """
    pass


class TextMessage(TextMessage):
    """
    A text message with string-only content.
    """
    pass


class MultiModalMessage(MultiModalMessage):
    pass


class StopMessage(StopMessage):
    pass


class HandoffMessage(HandoffMessage):
    pass


class ToolCallRequestEvent(ToolCallRequestEvent):
    pass


class ToolCallExecutionEvent(ToolCallExecutionEvent):
    pass


class ToolCallSummaryMessage(ToolCallSummaryMessage):
    pass


class UserInputRequestedEvent(UserInputRequestedEvent):
    pass


class MemoryQueryEvent(MemoryQueryEvent):
    pass


class ModelClientStreamingChunkEvent(ModelClientStreamingChunkEvent):
    pass


class ThoughtEvent(ThoughtEvent):
    pass
