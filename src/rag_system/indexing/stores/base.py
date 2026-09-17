"""IndexStore interface."""

from __future__ import annotations

from typing import Protocol

from rag_system.models.index import IndexRecord


class IndexStore(Protocol):
    """Persist IndexRecords."""

    def upsert(self, records: list[IndexRecord]) -> None: ...
