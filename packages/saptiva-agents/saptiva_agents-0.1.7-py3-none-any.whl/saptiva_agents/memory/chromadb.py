from autogen_ext.memory.chromadb import ChromaDBVectorMemoryConfig, PersistentChromaDBVectorMemoryConfig, \
    HttpChromaDBVectorMemoryConfig, ChromaDBVectorMemory, SentenceTransformerEmbeddingFunctionConfig


class ChromaDBVectorMemoryConfig(ChromaDBVectorMemoryConfig):
    """Base configuration for ChromaDB-based memory implementation."""
    pass


class PersistentChromaDBVectorMemoryConfig(PersistentChromaDBVectorMemoryConfig):
    """Configuration for persistent ChromaDB memory."""
    pass


class HttpChromaDBVectorMemoryConfig(HttpChromaDBVectorMemoryConfig):
    """Configuration for HTTP ChromaDB memory."""
    pass


class ChromaDBVectorMemory(ChromaDBVectorMemory):
    """
    Store and retrieve memory using vector similarity search powered by ChromaDB.

    `ChromaDBVectorMemory` provides a vector-based memory implementation that uses ChromaDB for
    storing and retrieving content based on semantic similarity. It enhances agents with the ability
    to recall contextually relevant information during conversations by leveraging vector embeddings
    to find similar content.

    This implementation serves as a reference for more complex memory systems using vector embeddings.
    For advanced use cases requiring specialized formatting of retrieved content, users should extend
    this class and override the `update_context()` method.

    Args:
        config (ChromaDBVectorMemoryConfig | None): Configuration for the ChromaDB memory.
            If None, defaults to a PersistentChromaDBVectorMemoryConfig with default values.
            Two config types are supported:
            - PersistentChromaDBVectorMemoryConfig: For local storage
            - HttpChromaDBVectorMemoryConfig: For connecting to a remote ChromaDB server

    Example:

        .. code-block:: python

            import os
            from pathlib import Path
            from saptiva_agents import SAPTIVA_OPS
            from saptiva_agents.agents import AssistantAgent
            from saptiva_agents.memory import MemoryContent, MemoryMimeType
            from saptiva_agents.memory.chromadb import ChromaDBVectorMemory, PersistentChromaDBVectorMemoryConfig
            from saptiva_agents.base import SaptivaAIChatCompletionClient

            # Initialize ChromaDB memory with custom config
            memory = ChromaDBVectorMemory(
                config=PersistentChromaDBVectorMemoryConfig(
                    collection_name="user_preferences",
                    persistence_path=os.path.join(str(Path.home()), ".chromadb_autogen"),
                    k=3,  # Return top 3 results
                    score_threshold=0.5,  # Minimum similarity score
                )
            )

            # Add user preferences to memory
            await memory.add(
                MemoryContent(
                    content="The user prefers temperatures in Celsius",
                    mime_type=MemoryMimeType.TEXT,
                    metadata={"category": "preferences", "type": "units"},
                )
            )

            # Create assistant agent with ChromaDB memory
            assistant = AssistantAgent(
                name="assistant",
                model_client=SaptivaAIChatCompletionClient(
                    model=SAPTIVA_OPS,
                    api_key="TU_SAPTIVA_API_KEY",
                ),
                memory=[memory]
            )

            # The memory will automatically retrieve relevant content during conversations
            stream = assistant.run_stream(task="What's the weather in New York?")

            # Remember to close the memory when finished
            await memory.close()
    """
    pass


class SentenceTransformerEmbeddingFunctionConfig(SentenceTransformerEmbeddingFunctionConfig):
    """Configuration for SentenceTransformerEmbeddingFunction."""
    pass

