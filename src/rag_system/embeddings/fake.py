"""Deterministic, offline embedder for tests and demos."""

from __future__ import annotations

import hashlib


class FakeEmbedder:
    """Produce stable vectors without network access.

    Vectors are derived deterministically from the text via hashing, so the
    same text always yields the same vector. Quality is intentionally poor;
    this only validates the data flow.
    """

    def __init__(self, dimension: int = 8):
        if dimension <= 0:
            raise ValueError("dimension must be a positive integer")
        self.dimension = dimension

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [digest[i % len(digest)] / 255.0 for i in range(self.dimension)]
