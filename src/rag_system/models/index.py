"""Index data model: IndexRecord."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IndexRecord:
    """A chunk plus its machine-comparable vector representation."""

    id: str
    chunk_id: str
    document_id: str
    content: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
