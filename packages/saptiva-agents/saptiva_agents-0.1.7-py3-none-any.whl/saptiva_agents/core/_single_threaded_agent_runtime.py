from autogen_core import SingleThreadedAgentRuntime


class SingleThreadedAgentRuntime(SingleThreadedAgentRuntime):
    """A single-threaded agent runtime that processes all messages using a single asyncio queue.
    Messages are delivered in the order they are received, and the runtime processes
    each message in a separate asyncio task concurrently.
    """
    pass
