"""Parser interface."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from rag_system.models.document import Document


class Parser(Protocol):
    """Convert a raw source into a unified Document."""

    def parse(self, source: Path) -> Document: ...
