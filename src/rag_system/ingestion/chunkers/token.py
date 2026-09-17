"""Token-based chunker."""

from __future__ import annotations

import uuid

from rag_system.ingestion.tokenizers.base import Tokenizer
from rag_system.models.chunk import Chunk
from rag_system.models.document import Block, Document

_SEPARATOR = "\n\n"


class TokenChunker:
    """Aggregate blocks into token-bounded chunks; split oversized blocks.

    Normal block aggregation preserves block boundaries and applies no overlap.
    A single block larger than ``max_tokens`` is split into token windows with
    ``overlap_tokens`` overlap between consecutive windows.
    """

    def __init__(
        self,
        tokenizer: Tokenizer,
        max_tokens: int = 512,
        overlap_tokens: int = 50,
    ):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be a positive integer")
        if overlap_tokens < 0:
            raise ValueError("overlap_tokens must be >= 0")
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be < max_tokens")
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        current: list[Block] = []
        current_tokens = 0

        def flush() -> None:
            nonlocal current, current_tokens
            if current:
                chunks.append(self._make_chunk(document, current, len(chunks)))
                current = []
                current_tokens = 0

        for block in document.blocks:
            block_tokens = self.tokenizer.encode(block.text)
            token_count = len(block_tokens)

            if token_count > self.max_tokens:
                flush()
                self._split_block(document, block, chunks)
                continue

            if not current:
                current.append(block)
                current_tokens = token_count
                continue

            sep_tokens = len(self.tokenizer.encode(_SEPARATOR))
            would_be = current_tokens + sep_tokens + token_count
            if would_be > self.max_tokens:
                flush()
                current.append(block)
                current_tokens = token_count
            else:
                current.append(block)
                current_tokens = would_be

        flush()
        return chunks

    def _split_block(
        self,
        document: Document,
        block: Block,
        chunks: list[Chunk],
    ) -> None:
        tokens = self.tokenizer.encode(block.text)
        step = self.max_tokens - self.overlap_tokens
        start = 0
        while start < len(tokens):
            end = min(start + self.max_tokens, len(tokens))
            text = self.tokenizer.decode(tokens[start:end])
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    content=text,
                    block_ids=[block.id],
                    order=len(chunks),
                )
            )
            start += step

    @staticmethod
    def _make_chunk(
        document: Document,
        blocks: list[Block],
        order: int,
    ) -> Chunk:
        return Chunk(
            id=str(uuid.uuid4()),
            document_id=document.id,
            content=_SEPARATOR.join(block.text for block in blocks),
            block_ids=[block.id for block in blocks],
            order=order,
        )
