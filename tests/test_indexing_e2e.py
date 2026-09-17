"""V1 end-to-end test: sample.md -> chunks -> vectors -> index.jsonl."""

from pathlib import Path

from rag_system.embeddings.fake import FakeEmbedder
from rag_system.indexing.indexer import Indexer
from rag_system.indexing.stores.jsonl import JsonlIndexStore
from rag_system.ingestion.chunkers.token import TokenChunker
from rag_system.ingestion.parsers.markdown import MarkdownParser

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_v1_end_to_end(tmp_path, tokenizer):
    parser = MarkdownParser()
    chunker = TokenChunker(tokenizer=tokenizer, max_tokens=100, overlap_tokens=0)
    store = JsonlIndexStore(tmp_path / "index.jsonl")
    indexer = Indexer(embedder=FakeEmbedder(dimension=4), store=store)

    document = parser.parse(FIXTURES / "sample.md")
    chunks = chunker.chunk(document)
    records = indexer.index(chunks)

    assert chunks
    assert len(records) == len(chunks)
    assert {r.document_id for r in records} == {document.id}

    lines = store.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(chunks)
