"""Indexer orchestration: chunks -> vectors -> records -> store."""

from __future__ import annotations

from rag_system.embeddings.base import Embedder
from rag_system.indexing.stores.base import IndexStore
from rag_system.models.chunk import Chunk
from rag_system.models.index import IndexRecord


class Indexer:
    """Embed chunks and persist the resulting IndexRecords."""

    def __init__(self, embedder: Embedder, store: IndexStore):
        self.embedder = embedder
        self.store = store

    def index(self, chunks: list[Chunk]) -> list[IndexRecord]:
        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]
        vectors = self.embedder.embed_documents(texts)
        if len(vectors) != len(chunks):
            raise ValueError(
                f"embedder returned {len(vectors)} vectors for {len(chunks)} chunks"
            )

        records = [
            IndexRecord(
                id=chunk.id,
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                vector=vector,
                metadata=dict(chunk.metadata),
            )
            for chunk, vector in zip(chunks, vectors)
        ]

        self.store.upsert(records)
        return records
