"""Tests for the end-to-end ingestion pipeline."""

from pathlib import Path

from rag_system.ingestion.chunkers.simple import SimpleChunker
from rag_system.ingestion.parsers.markdown import MarkdownParser
from rag_system.pipeline import IngestionPipeline

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_pipeline_end_to_end():
    pipeline = IngestionPipeline(
        parser=MarkdownParser(),
        chunker=SimpleChunker(max_chars=1000),
    )

    chunks = pipeline.run(FIXTURES / "sample.md")

    assert len(chunks) >= 1
    assert len({c.document_id for c in chunks}) == 1
    assert all(c.block_ids for c in chunks)
    assert chunks[0].content.startswith("Agent Memory")
    assert "Short-term memory stores session context." in chunks[-1].content


def test_pipeline_accepts_string_path():
    pipeline = IngestionPipeline(
        parser=MarkdownParser(),
        chunker=SimpleChunker(),
    )

    chunks = pipeline.run(str(FIXTURES / "sample.md"))
    assert chunks
