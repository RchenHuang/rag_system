"""RAG system — V0: unified ingestion pipeline (Parser -> Chunker)."""

from rag_system.ingestion.chunkers.simple import SimpleChunker
from rag_system.ingestion.parsers.markdown import MarkdownParser
from rag_system.models.chunk import Chunk
from rag_system.models.document import Block, Document
from rag_system.pipeline import IngestionPipeline

__all__ = [
    "Block",
    "Document",
    "Chunk",
    "MarkdownParser",
    "SimpleChunker",
    "IngestionPipeline",
]
