"""Core data model: Chunk."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """Basic knowledge unit handed to a future retrieval system."""

    id: str
    document_id: str
    content: str
    block_ids: list[str]
    order: int
    metadata: dict[str, Any] = field(default_factory=dict)
