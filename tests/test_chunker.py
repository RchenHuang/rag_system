"""Tests for SimpleChunker."""

import uuid

import pytest

from rag_system.ingestion.chunkers.simple import SimpleChunker
from rag_system.models.document import Block, Document


def make_block(text: str, order: int) -> Block:
    return Block(
        id=str(uuid.uuid4()),
        type="paragraph",
        text=text,
        order=order,
    )


def make_document(*texts: str) -> Document:
    blocks = [make_block(text, i) for i, text in enumerate(texts)]
    return Document(
        id=str(uuid.uuid4()),
        source="memory.md",
        filename="memory.md",
        mime_type="text/markdown",
        blocks=blocks,
    )


def test_single_chunk_under_max_chars():
    doc = make_document("A", "B", "C")

    chunks = SimpleChunker(max_chars=1000).chunk(doc)

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.document_id == doc.id
    assert chunk.block_ids == [b.id for b in doc.blocks]
    assert chunk.order == 0
    assert chunk.content == "A\n\nB\n\nC"


def test_splits_when_over_max_chars():
    doc = make_document("A" * 10, "B" * 10, "C" * 10)

    # A(10) + sep(2) + B(10) = 22 fits; adding C (22 + 2 + 10 = 34) does not.
    chunks = SimpleChunker(max_chars=30).chunk(doc)

    assert len(chunks) == 2
    assert [c.order for c in chunks] == [0, 1]
    assert chunks[0].block_ids == [doc.blocks[0].id, doc.blocks[1].id]
    assert chunks[1].block_ids == [doc.blocks[2].id]
    assert chunks[0].content == "A" * 10 + "\n\n" + "B" * 10
    assert chunks[1].content == "C" * 10


def test_oversized_block_is_not_split():
    doc = make_document("X" * 50, "Y")

    chunks = SimpleChunker(max_chars=10).chunk(doc)

    assert len(chunks) == 2
    assert chunks[0].content == "X" * 50
    assert chunks[1].content == "Y"


def test_empty_document_produces_no_chunks():
    assert SimpleChunker().chunk(make_document()) == []


def test_max_chars_must_be_positive():
    with pytest.raises(ValueError):
        SimpleChunker(max_chars=0)
