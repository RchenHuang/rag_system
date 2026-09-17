"""Tests for MarkdownParser."""

from pathlib import Path

from rag_system.ingestion.parsers.markdown import MarkdownParser

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_parse_sample_blocks():
    doc = MarkdownParser().parse(FIXTURES / "sample.md")

    assert doc is not None
    assert len(doc.blocks) == 4

    b0, b1, b2, b3 = doc.blocks

    assert b0.type == "heading"
    assert b0.text == "Agent Memory"
    assert b0.heading_level == 1
    assert b0.order == 0

    assert b1.type == "paragraph"
    assert b1.text == "Agent memory contains short-term memory."
    assert b1.heading_level is None
    assert b1.order == 1

    assert b2.type == "heading"
    assert b2.text == "Short-term Memory"
    assert b2.heading_level == 2
    assert b2.order == 2

    assert b3.type == "paragraph"
    assert b3.text == "Short-term memory stores session context."
    assert b3.heading_level is None
    assert b3.order == 3


def test_parse_document_fields():
    doc = MarkdownParser().parse(FIXTURES / "sample.md")

    assert doc.filename == "sample.md"
    assert doc.mime_type == "text/markdown"
    assert doc.source.endswith("sample.md")
    assert doc.metadata == {}
    assert doc.id

    ids = [block.id for block in doc.blocks]
    assert len(ids) == len(set(ids))


def test_paragraph_merging_and_h3(tmp_path):
    path = tmp_path / "multi.md"
    path.write_text(
        "# Title\n\nPara line one\nline two\n\n### Sub\n\nAfter\n",
        encoding="utf-8",
    )

    doc = MarkdownParser().parse(path)

    assert [b.type for b in doc.blocks] == [
        "heading",
        "paragraph",
        "heading",
        "paragraph",
    ]
    assert doc.blocks[1].text == "Para line one line two"
    assert doc.blocks[2].heading_level == 3
    assert doc.blocks[3].text == "After"
