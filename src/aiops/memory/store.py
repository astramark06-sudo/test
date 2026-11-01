"""Local memory facade backed by SQLite FTS5 or LIKE search."""
from typing import Any
from aiops.storage.sqlite import SQLiteStore

class MemoryStore:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store
    def remember(self, title: str, body: str, namespace: str = "default", metadata: dict[str, Any] | None = None) -> int:
        return self.store.add_memory(namespace, title, body, metadata)
    def retrieve(self, query: str, namespace: str = "default", limit: int = 8) -> list[dict[str, Any]]:
        return self.store.search_memory(query, namespace, limit)
