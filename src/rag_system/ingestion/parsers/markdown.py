"""Markdown parser: extract heading/paragraph blocks from a .md file."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from rag_system.models.document import Block, Document

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

_MIME_TYPE = "text/markdown"


class MarkdownParser:
    """Parse a Markdown file into a Document.

    V0 only reliably recognizes ATX headings (``#``, ``##``, ``###``) and
    paragraphs. Everything else is treated as plain paragraph text.
    """

    def parse(self, source: Path) -> Document:
        text = source.read_text(encoding="utf-8")
        return Document(
            id=str(uuid.uuid4()),
            source=str(source),
            filename=source.name,
            mime_type=_MIME_TYPE,
            blocks=self._parse_blocks(text),
        )

    @staticmethod
    def _parse_blocks(text: str) -> list[Block]:
        blocks: list[Block] = []
        order = 0
        lines = text.splitlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            heading = _HEADING_RE.match(line)
            if heading:
                blocks.append(
                    Block(
                        id=str(uuid.uuid4()),
                        type="heading",
                        text=heading.group(2),
                        order=order,
                        heading_level=len(heading.group(1)),
                    )
                )
                order += 1
                i += 1
                continue

            # Paragraph: merge consecutive non-blank, non-heading lines.
            paragraph = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or _HEADING_RE.match(nxt):
                    break
                paragraph.append(nxt)
                i += 1

            blocks.append(
                Block(
                    id=str(uuid.uuid4()),
                    type="paragraph",
                    text=" ".join(paragraph),
                    order=order,
                )
            )
            order += 1

        return blocks
