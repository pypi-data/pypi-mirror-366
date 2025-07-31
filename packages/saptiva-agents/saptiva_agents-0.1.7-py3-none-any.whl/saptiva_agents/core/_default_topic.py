from autogen_core import DefaultTopicId


class DefaultTopicId(DefaultTopicId):
    """DefaultTopicId provides a sensible default for the topic_id and source fields of a TopicId.

    If created in the context of a message handler, the source will be set to the agent_id of the message handler, otherwise it will be set to "default".

    Args:
        type (str, optional): Topic type to publish message to. Defaults to "default".
        source (str | None, optional): Topic source to publish message to. If None, the source will be set to the agent_id of the message handler if in the context of a message handler, otherwise it will be set to "default". Defaults to None.
    """
    pass
