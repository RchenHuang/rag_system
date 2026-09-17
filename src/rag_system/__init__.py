"""RAG system — V1: ingestion (Parser -> Chunker) + indexing (Embedder -> IndexStore)."""

from rag_system.embeddings.fake import FakeEmbedder
from rag_system.embeddings.openai_compatible import OpenAICompatibleEmbedder
from rag_system.indexing.indexer import Indexer
from rag_system.indexing.stores.jsonl import JsonlIndexStore
from rag_system.ingestion.chunkers.simple import SimpleChunker
from rag_system.ingestion.chunkers.token import TokenChunker
from rag_system.ingestion.parsers.markdown import MarkdownParser
from rag_system.ingestion.tokenizers.tiktoken import TiktokenTokenizer
from rag_system.models.chunk import Chunk
from rag_system.models.document import Block, Document
from rag_system.models.index import IndexRecord
from rag_system.pipelines.indexing import IndexingPipeline
from rag_system.pipelines.ingestion import IngestionPipeline

__all__ = [
    "Block",
    "Document",
    "Chunk",
    "IndexRecord",
    "MarkdownParser",
    "SimpleChunker",
    "TokenChunker",
    "TiktokenTokenizer",
    "FakeEmbedder",
    "OpenAICompatibleEmbedder",
    "Indexer",
    "JsonlIndexStore",
    "IngestionPipeline",
    "IndexingPipeline",
]
