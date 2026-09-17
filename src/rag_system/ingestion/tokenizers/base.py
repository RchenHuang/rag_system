"""Tokenizer interface."""

from __future__ import annotations

from typing import Protocol


class Tokenizer(Protocol):
    """Convert text to token ids and back."""

    def encode(self, text: str) -> list[int]: ...

    def decode(self, tokens: list[int]) -> str: ...
