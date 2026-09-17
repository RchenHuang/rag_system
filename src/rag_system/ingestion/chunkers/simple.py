"""Simple block-aggregating chunker."""

from __future__ import annotations

import uuid

from rag_system.models.chunk import Chunk
from rag_system.models.document import Block, Document

_SEPARATOR = "\n\n"


class SimpleChunker:
    """Aggregate blocks into chunks up to ``max_chars`` without splitting a block."""

    def __init__(self, max_chars: int = 1000):
        if max_chars <= 0:
            raise ValueError("max_chars must be a positive integer")
        self.max_chars = max_chars

    def chunk(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        current: list[Block] = []
        current_length = 0

        for block in document.blocks:
            block_length = len(block.text)

            if not current:
                current.append(block)
                current_length = block_length
                continue

            would_be = current_length + len(_SEPARATOR) + block_length
            if would_be > self.max_chars:
                chunks.append(self._make_chunk(document, current, len(chunks)))
                current = [block]
                current_length = block_length
            else:
                current.append(block)
                current_length = would_be

        if current:
            chunks.append(self._make_chunk(document, current, len(chunks)))

        return chunks

    @staticmethod
    def _make_chunk(document: Document, blocks: list[Block], order: int) -> Chunk:
        return Chunk(
            id=str(uuid.uuid4()),
            document_id=document.id,
            content=_SEPARATOR.join(block.text for block in blocks),
            block_ids=[block.id for block in blocks],
            order=order,
        )
