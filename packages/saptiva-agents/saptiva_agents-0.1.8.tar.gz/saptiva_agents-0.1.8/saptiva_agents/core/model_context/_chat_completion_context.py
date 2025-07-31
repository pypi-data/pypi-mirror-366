from autogen_core.model_context import ChatCompletionContext


class ChatCompletionContext(ChatCompletionContext):
    """An abstract base class for defining the interface of a chat completion context.
    A chat completion context lets agents store and retrieve LLM messages.
    It can be implemented with different recall strategies.

    Args:
        initial_messages (List[LLMMessage] | None): The initial messages.
    """
    pass

