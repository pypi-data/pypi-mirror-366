from autogen_core.models import ChatCompletionClient


class ChatCompletionClient(ChatCompletionClient):
    # Caching has to be handled internally as they can depend on the create args that were stored in the constructor
    pass
