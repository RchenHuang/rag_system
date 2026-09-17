"""Configuration loaded from environment variables (and optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class EmbeddingConfig:
    """Embedding provider configuration.

    Values come from environment variables:
        EMBEDDING_BASE_URL
        EMBEDDING_API_KEY
        EMBEDDING_MODEL
    """

    base_url: str
    api_key: str
    model: str

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        load_dotenv()
        return cls(
            base_url=os.getenv("EMBEDDING_BASE_URL", ""),
            api_key=os.getenv("EMBEDDING_API_KEY", ""),
            model=os.getenv("EMBEDDING_MODEL", ""),
        )
