from saptiva_agents import CONTEXT_MAX_ITEMS
from saptiva_agents.memory import MemoryContent, ListMemory


class MemoryManager:
    """
    Simple wrapper for managing memory with limits

    Example:
        from saptiva_agents.memory import MemoryManager, ListMemory, MemoryContent


        async def demo_memory_manager():
            memory = ListMemory(name="managed_memory")
            manager = MemoryManager(memory, max_items=3)

            # Test con diferentes mensajes
            test_messages = [
                "Mensaje 1", "Mensaje 2", "Mensaje 3",
                "Mensaje 4", "Mensaje 5", "Mensaje 6"
            ]

            for msg in test_messages:
                content = MemoryContent(content=msg, mime_type="text/plain")
                await manager.add(content)

                print(f"Agregado: {msg}")
                print(f"Count: {manager.current_count}, Full: {manager.is_full}")
                print(f"Contenido: {[item.content for item in memory.content]}")
                print()

            # Cambiar límite
            print("Cambiando límite a 5...")
            manager.set_limit(5)

            # Agregar más
            for i in range(3):
                content = MemoryContent(content=f"Extra {i + 1}", mime_type="text/plain")
                await manager.add(content)

            print(f"Final: {[item.content for item in memory.content]}")

        asyncio.run(demo_memory_manager())

    """

    def __init__(self, memory: ListMemory, max_items: int = CONTEXT_MAX_ITEMS):
        self.memory = memory
        self.max_items = max_items

    async def add(self, content: MemoryContent) -> None:
        """
        Add content with an automatic limit
        """
        await self.memory.add(content)
        self._apply_limit()

    def _apply_limit(self) -> None:
        """
        Apply the limit keeping the last N elements
        """
        if len(self.memory.content) > self.max_items:
            self.memory.content = self.memory.content[-self.max_items:]

    def set_limit(self, new_limit: int) -> None:
        """
        Change the limit and apply it immediately
        """
        self.max_items = new_limit
        self._apply_limit()

    @property
    def current_count(self) -> int:
        """
        Check the current count of items in the memory
        """
        return len(self.memory.content)

    @property
    def is_full(self) -> bool:
        """
        Check if the memory is full
        """
        return len(self.memory.content) >= self.max_items