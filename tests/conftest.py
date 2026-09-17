"""Shared test fixtures."""

import pytest


class CharTokenizer:
    """Deterministic offline tokenizer: one token per character.

    Satisfies the Tokenizer protocol (encode/decode) and round-trips exactly.
    """

    def encode(self, text: str) -> list[int]:
        return [ord(ch) for ch in text]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(token) for token in tokens)


@pytest.fixture
def tokenizer() -> CharTokenizer:
    return CharTokenizer()
