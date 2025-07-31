from autogen_core.memory import Memory, MemoryContent, ListMemory


class MemoryContent(MemoryContent):
    """A memory content item."""
    pass


class Memory(Memory):
    """Protocol defining the interface for memory implementations.

    A memory is the storage for data that can be used to enrich or modify the model context.

    A memory implementation can use any storage mechanism, such as a list, a database, or a file system.
    It can also use any retrieval mechanism, such as vector search or text search.
    It is up to the implementation to decide how to store and retrieve data.

    It is also a memory implementation's responsibility to update the model context
    with relevant memory content based on the current model context and querying the memory store.

    See :class:`~saptiva_agents.memory.ListMemory` for an example implementation.
    """
    pass


def limit_memory_to_last_n(memory: ListMemory, n: int) -> ListMemory:
    """
    Limit memory to the last N elements using the content property.

    Args:
        memory: ListMemory instance
        n: Number of elements to keep

    Returns:
        memory: ListMemory instance with limited content
    """
    if len(memory.content) > n:
        memory.content = memory.content[-n:]

    return memory
