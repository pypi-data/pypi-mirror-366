from autogen_agentchat.agents import BaseChatAgent


class BaseChatAgent(BaseChatAgent):
    """
    Base class for a chat agent.

    This abstract class provides a base implementation for a :class:`ChatAgent`.
    To create a new chat agent, subclass this class and implement the
    :meth:`on_messages`, :meth:`on_reset`, and :attr:`produced_message_types`.
    If streaming is required, also implement the :meth:`on_messages_stream` method.

    An agent is considered stateful and maintains its state between calls to
    the :meth:`on_messages` or :meth:`on_messages_stream` methods.
    The agent should store its state in the
    agent instance. The agent should also implement the :meth:`on_reset` method
    to reset the agent to its initialization state.

    .. note::

        The caller should only pass the new messages to the agent on each call
        to the :meth:`on_messages` or :meth:`on_messages_stream` method.
        Do not pass the entire conversation history to the agent on each call.
        This design principle must be followed when creating a new agent.
    """
    pass