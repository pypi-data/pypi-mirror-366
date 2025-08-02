"""Configuration and directory management for LitAI."""

from pathlib import Path

from structlog import get_logger

logger = get_logger()


class Config:
    """Manages LitAI configuration and directory structure."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize config with base directory.

        Args:
            base_dir: Base directory for LitAI data. Defaults to ~/.litai
        """
        if base_dir is None:
            base_dir = Path.home() / ".litai"
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.base_dir,
            self.pdfs_dir,
            self.db_dir,
        ]

        for dir_path in directories:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info("Created directory", path=str(dir_path))

    @property
    def pdfs_dir(self) -> Path:
        """Directory for storing downloaded PDFs."""
        return self.base_dir / "pdfs"

    @property
    def db_dir(self) -> Path:
        """Directory for database files."""
        return self.base_dir / "db"

    @property
    def db_path(self) -> Path:
        """Path to the SQLite database file."""
        return self.db_dir / "litai.db"

    def pdf_path(self, paper_id: str) -> Path:
        """Get the path for a specific paper's PDF.

        Args:
            paper_id: Unique identifier for the paper

        Returns:
            Path where the PDF should be stored
        """
        return self.pdfs_dir / f"{paper_id}.pdf"
