"""Data models for LitAI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import json


@dataclass
class Paper:
    """Represents a research paper."""

    paper_id: str
    title: str
    authors: list[str]
    year: int
    abstract: str
    arxiv_id: str | None = None
    doi: str | None = None
    citation_count: int = 0
    tldr: str | None = None
    venue: str | None = None
    open_access_pdf_url: str | None = None
    added_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": json.dumps(self.authors),
            "year": self.year,
            "abstract": self.abstract,
            "arxiv_id": self.arxiv_id,
            "doi": self.doi,
            "citation_count": self.citation_count,
            "tldr": self.tldr,
            "venue": self.venue,
            "open_access_pdf_url": self.open_access_pdf_url,
            "added_at": self.added_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Paper":
        """Create Paper from dictionary."""
        data = data.copy()
        if isinstance(data.get("authors"), str):
            data["authors"] = json.loads(data["authors"])
        if isinstance(data.get("added_at"), str):
            data["added_at"] = datetime.fromisoformat(data["added_at"])
        return cls(**data)


@dataclass
class Extraction:
    """Represents an extracted piece of information from a paper."""

    paper_id: str
    extraction_type: str  # e.g., "key_points", "methodology", "results"
    content: dict[str, Any]  # Flexible JSON content
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "paper_id": self.paper_id,
            "extraction_type": self.extraction_type,
            "content": json.dumps(self.content),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Extraction":
        """Create Extraction from dictionary."""
        data = data.copy()
        if isinstance(data.get("content"), str):
            data["content"] = json.loads(data["content"])
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        # Remove database-specific fields
        data.pop("id", None)
        return cls(**data)
