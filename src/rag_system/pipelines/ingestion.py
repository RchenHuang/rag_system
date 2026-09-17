"""Ingestion pipeline orchestration."""

from __future__ import annotations

from pathlib import Path

from rag_system.ingestion.chunkers.base import Chunker
from rag_system.ingestion.parsers.base import Parser
from rag_system.models.chunk import Chunk


class IngestionPipeline:
    """Orchestrate parser -> chunker without knowing implementation details."""

    def __init__(self, parser: Parser, chunker: Chunker):
        self.parser = parser
        self.chunker = chunker

    def run(self, source: str | Path) -> list[Chunk]:
        document = self.parser.parse(Path(source))
        return self.chunker.chunk(document)
