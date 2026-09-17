"""Chunker interface."""

from __future__ import annotations

from typing import Protocol

from rag_system.models.chunk import Chunk
from rag_system.models.document import Document


class Chunker(Protocol):
    """Split a Document into a list of Chunks."""

    def chunk(self, document: Document) -> list[Chunk]: ...
