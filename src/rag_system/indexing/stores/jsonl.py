"""JSONL-backed local index store."""

from __future__ import annotations

import json
from pathlib import Path

from rag_system.models.index import IndexRecord


class JsonlIndexStore:
    """Persist records as JSON Lines, overwriting the file on each upsert."""

    def __init__(self, path: str | Path = "data/index.jsonl"):
        self.path = Path(path)

    def upsert(self, records: list[IndexRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(self._to_dict(record), ensure_ascii=False) + "\n")

    @staticmethod
    def _to_dict(record: IndexRecord) -> dict:
        return {
            "id": record.id,
            "chunk_id": record.chunk_id,
            "document_id": record.document_id,
            "content": record.content,
            "vector": record.vector,
            "metadata": record.metadata,
        }
