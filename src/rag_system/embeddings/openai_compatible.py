"""OpenAI-compatible embedding client."""

from __future__ import annotations

from openai import OpenAI

from rag_system.config import EmbeddingConfig


class OpenAICompatibleEmbedder:
    """Embed texts via any OpenAI-compatible embeddings endpoint."""

    def __init__(self, base_url: str, api_key: str, model: str):
        if not base_url or not api_key or not model:
            raise ValueError("base_url, api_key, and model must all be set")
        self.base_url = base_url
        self.model = model
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    @classmethod
    def from_env(cls) -> "OpenAICompatibleEmbedder":
        cfg = EmbeddingConfig.from_env()
        return cls(base_url=cfg.base_url, api_key=cfg.api_key, model=cfg.model)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]
