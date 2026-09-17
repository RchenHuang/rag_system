"""Tiktoken-backed tokenizer."""

from __future__ import annotations

import tiktoken


class TiktokenTokenizer:
    """Tokenize text using a tiktoken encoding."""

    def __init__(self, encoding: str = "cl100k_base"):
        self.encoding_name = encoding
        self._encoding = tiktoken.get_encoding(encoding)

    def encode(self, text: str) -> list[int]:
        return self._encoding.encode(text)

    def decode(self, tokens: list[int]) -> str:
        return self._encoding.decode(tokens)
