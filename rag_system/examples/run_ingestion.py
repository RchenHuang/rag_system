"""Run the V0 ingestion pipeline and print the data flow.

Usage:
    python examples/run_ingestion.py            # uses tests/fixtures/sample.md
    python examples/run_ingestion.py some.md    # any .md file
"""

from __future__ import annotations

import sys
from pathlib import Path

from rag_system import IngestionPipeline, MarkdownParser, SimpleChunker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE = PROJECT_ROOT / "tests" / "fixtures" / "sample.md"


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SAMPLE

    parser = MarkdownParser()
    pipeline = IngestionPipeline(parser=parser, chunker=SimpleChunker(max_chars=1000))

    document = parser.parse(source)
    chunks = pipeline.run(source)

    print("Document:")
    print(f"  id: {document.id}")
    print(f"  source: {document.source}")
    print(f"  filename: {document.filename}")
    print(f"  mime_type: {document.mime_type}")
    print(f"  blocks: {len(document.blocks)}")
    for block in document.blocks:
        if block.type == "heading":
            label = f"heading (h{block.heading_level})"
        else:
            label = "paragraph"
        print(f"    [{block.order}] {label}: {block.text!r}")

    print()
    print("Chunks:")
    for chunk in chunks:
        print()
        print(f"Chunk {chunk.order}")
        print("----------------")
        print(chunk.content)


if __name__ == "__main__":
    main()
