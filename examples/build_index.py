"""Build a persistent index from a Markdown file.

Usage:
    python examples/build_index.py [file.md] [output.jsonl]

Defaults to tests/fixtures/sample.md and data/index.jsonl. Uses FakeEmbedder
unless embedding credentials are configured via environment variables / .env.
"""

from __future__ import annotations

import sys
from pathlib import Path

from rag_system.config import EmbeddingConfig
from rag_system.embeddings.fake import FakeEmbedder
from rag_system.embeddings.openai_compatible import OpenAICompatibleEmbedder
from rag_system.indexing.indexer import Indexer
from rag_system.indexing.stores.jsonl import JsonlIndexStore
from rag_system.ingestion.chunkers.token import TokenChunker
from rag_system.ingestion.parsers.markdown import MarkdownParser
from rag_system.ingestion.tokenizers.tiktoken import TiktokenTokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE = PROJECT_ROOT / "tests" / "fixtures" / "sample.md"
DEFAULT_INDEX = PROJECT_ROOT / "data" / "index.jsonl"


def build_embedder():
    cfg = EmbeddingConfig.from_env()
    if cfg.base_url and cfg.api_key and cfg.model:
        return OpenAICompatibleEmbedder(
            base_url=cfg.base_url, api_key=cfg.api_key, model=cfg.model
        )
    return FakeEmbedder(dimension=8)


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLE
    index_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_INDEX

    parser = MarkdownParser()
    chunker = TokenChunker(tokenizer=TiktokenTokenizer())
    indexer = Indexer(embedder=build_embedder(), store=JsonlIndexStore(index_path))

    document = parser.parse(source)   # parse once
    chunks = chunker.chunk(document)  # chunk the same Document
    records = indexer.index(chunks)

    print("Document parsed")
    print(f"Chunks created: {len(chunks)}")
    print(f"Vectors generated: {len(records)}")
    print(f"Index records written: {len(records)}")
    print(f"Index path: {index_path}")


if __name__ == "__main__":
    main()
