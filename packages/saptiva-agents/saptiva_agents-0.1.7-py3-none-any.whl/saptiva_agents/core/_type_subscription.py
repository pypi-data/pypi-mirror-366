from autogen_core import TypeSubscription


class TypeSubscription(TypeSubscription):
    """This subscription matches on topics based on the type and maps to agents using the source of the topic as the agent key.

    This subscription causes each source to have its own agent instance.

    Example:

        .. code-block:: python

            from saptiva_agents.core import TypeSubscription

            subscription = TypeSubscription(topic_type="t1", agent_type="a1")

        In this case:

        - A topic_id with type `t1` and source `s1` will be handled by an agent of type `a1` with key `s1`
        - A topic_id with type `t1` and source `s2` will be handled by an agent of type `a1` with key `s2`.

    Args:
        topic_type (str): Topic type to match against
        agent_type (str): Agent type to handle this subscription
    """
    pass
