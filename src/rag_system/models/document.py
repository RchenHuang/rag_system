"""Core data models: Document and Block."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

BlockType = Literal["heading", "paragraph"]


@dataclass
class Block:
    """Smallest structured content unit extracted by a parser."""

    id: str
    type: BlockType
    text: str
    order: int
    page: int | None = None
    heading_level: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type == "heading" and (
            self.heading_level is None or self.heading_level < 1
        ):
            raise ValueError(
                f"heading block must have heading_level >= 1, got {self.heading_level!r}"
            )


@dataclass
class Document:
    """A complete document converted to the unified internal format."""

    id: str
    source: str
    filename: str
    mime_type: str | None
    blocks: list[Block]
    metadata: dict[str, Any] = field(default_factory=dict)
