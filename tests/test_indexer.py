"""Tests for Indexer."""

import uuid

from rag_system.embeddings.fake import FakeEmbedder
from rag_system.indexing.indexer import Indexer
from rag_system.indexing.stores.jsonl import JsonlIndexStore
from rag_system.models.chunk import Chunk


def make_chunk(text: str) -> Chunk:
    return Chunk(
        id=str(uuid.uuid4()),
        document_id="doc-1",
        content=text,
        block_ids=["block-1"],
        order=0,
    )


def test_indexer_creates_and_persists_records(tmp_path):
    chunks = [make_chunk("a"), make_chunk("b"), make_chunk("c")]
    store = JsonlIndexStore(tmp_path / "index.jsonl")
    indexer = Indexer(embedder=FakeEmbedder(dimension=4), store=store)

    records = indexer.index(chunks)

    assert len(records) == 3
    for record, chunk in zip(records, chunks):
        assert record.id == chunk.id
        assert record.chunk_id == chunk.id
        assert record.document_id == chunk.document_id
        assert record.content == chunk.content
        assert len(record.vector) == 4

    assert store.path.exists()
    lines = store.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 3
