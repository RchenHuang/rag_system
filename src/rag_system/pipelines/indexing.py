"""Indexing pipeline orchestration."""

from __future__ import annotations

from rag_system.indexing.indexer import Indexer
from rag_system.models.chunk import Chunk
from rag_system.models.index import IndexRecord


class IndexingPipeline:
    """Orchestrate chunks -> indexer -> persisted IndexRecords."""

    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def run(self, chunks: list[Chunk]) -> list[IndexRecord]:
        return self.indexer.index(chunks)
