"""Tests for JsonlIndexStore."""

import json

from rag_system.indexing.stores.jsonl import JsonlIndexStore
from rag_system.models.index import IndexRecord


def make_record() -> IndexRecord:
    return IndexRecord(
        id="r1",
        chunk_id="c1",
        document_id="d1",
        content="hello",
        vector=[0.1, 0.2],
        metadata={},
    )


def test_upsert_writes_file(tmp_path):
    path = tmp_path / "sub" / "index.jsonl"
    store = JsonlIndexStore(path)

    store.upsert([make_record()])

    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["chunk_id"] == "c1"
    assert data["content"] == "hello"
    assert data["vector"] == [0.1, 0.2]


def test_upsert_overwrites(tmp_path):
    path = tmp_path / "index.jsonl"
    store = JsonlIndexStore(path)

    store.upsert([make_record()])
    store.upsert([make_record()])

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1  # overwritten, not appended
