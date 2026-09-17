"""Embedder interface."""

from __future__ import annotations

from typing import Protocol


class Embedder(Protocol):
    """Convert a list of texts into a list of vectors (batch)."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
