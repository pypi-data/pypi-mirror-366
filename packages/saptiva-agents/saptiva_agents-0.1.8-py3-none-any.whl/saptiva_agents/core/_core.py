from autogen_core import CancellationToken, Image
from autogen_core.model_context import BufferedChatCompletionContext, UnboundedChatCompletionContext


class Image(Image):
    pass


class CancellationToken(CancellationToken):
    """A token used to cancel pending async calls"""
    pass


class BufferedChatCompletionContext(BufferedChatCompletionContext):
    """
    A buffered chat completion context that keeps a view of the last n messages,
        where n is the buffer size. The buffer size is set at initialization.

    Args:
        buffer_size (int): The size of the buffer.
        initial_messages (List[LLMMessage] | None): The initial messages.
    """
    pass


class UnboundedChatCompletionContext(UnboundedChatCompletionContext):
    """An unbounded chat completion context that keeps a view of the all the messages."""
    pass
