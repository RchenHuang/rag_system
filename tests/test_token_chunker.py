"""Tests for TokenChunker."""

import uuid

import pytest

from rag_system.ingestion.chunkers.token import TokenChunker
from rag_system.models.document import Block, Document


def make_block(text: str, order: int) -> Block:
    return Block(id=str(uuid.uuid4()), type="paragraph", text=text, order=order)


def make_document(*texts: str) -> Document:
    blocks = [make_block(text, i) for i, text in enumerate(texts)]
    return Document(
        id=str(uuid.uuid4()),
        source="m.md",
        filename="m.md",
        mime_type="text/markdown",
        blocks=blocks,
    )


def test_single_chunk_under_max_tokens(tokenizer):
    doc = make_document("abc", "def")

    chunks = TokenChunker(tokenizer=tokenizer, max_tokens=10, overlap_tokens=0).chunk(doc)

    assert len(chunks) == 1
    assert chunks[0].content == "abc\n\ndef"
    assert chunks[0].block_ids == [b.id for b in doc.blocks]


def test_splits_on_block_boundary(tokenizer):
    # "aaaa"(4) + sep(2) + "bbbb"(4) = 10 fits; adding "cccc" -> 10+2+4=16 > 12
    doc = make_document("aaaa", "bbbb", "cccc")

    chunks = TokenChunker(tokenizer=tokenizer, max_tokens=12, overlap_tokens=0).chunk(doc)

    assert len(chunks) == 2
    assert chunks[0].content == "aaaa\n\nbbbb"
    assert chunks[1].content == "cccc"
    assert chunks[0].block_ids == [doc.blocks[0].id, doc.blocks[1].id]
    assert chunks[1].block_ids == [doc.blocks[2].id]


def test_oversized_block_split_by_tokens(tokenizer):
    doc = make_document("abcdefghij")  # 10 chars = 10 tokens

    chunks = TokenChunker(tokenizer=tokenizer, max_tokens=4, overlap_tokens=0).chunk(doc)

    assert [c.content for c in chunks] == ["abcd", "efgh", "ij"]
    assert all(c.block_ids == [doc.blocks[0].id] for c in chunks)


def test_oversized_block_overlap(tokenizer):
    doc = make_document("abcdef")  # 6 tokens

    chunks = TokenChunker(
        tokenizer=tokenizer, max_tokens=5, overlap_tokens=2
    ).chunk(doc)

    # step = max_tokens - overlap_tokens = 3
    # windows: [0,5) -> "abcde", [3,6) -> "def" (share "de")
    assert [c.content for c in chunks] == ["abcde", "def"]
    assert chunks[0].block_ids == [doc.blocks[0].id]
    assert chunks[1].block_ids == [doc.blocks[0].id]


def test_document_id_and_order_consistent(tokenizer):
    doc = make_document("x" * 10, "y" * 10, "z" * 10)

    chunks = TokenChunker(tokenizer=tokenizer, max_tokens=12, overlap_tokens=0).chunk(doc)

    assert len(chunks) == 3
    assert [c.order for c in chunks] == [0, 1, 2]
    assert all(c.document_id == doc.id for c in chunks)
    assert [c.block_ids for c in chunks] == [
        [doc.blocks[0].id],
        [doc.blocks[1].id],
        [doc.blocks[2].id],
    ]


def test_invalid_overlap(tokenizer):
    with pytest.raises(ValueError):
        TokenChunker(tokenizer=tokenizer, max_tokens=5, overlap_tokens=5)
