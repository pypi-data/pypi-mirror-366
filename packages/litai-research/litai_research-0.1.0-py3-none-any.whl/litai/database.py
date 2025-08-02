"""Database management for LitAI."""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from structlog import get_logger

from .models import Paper, Extraction
from .config import Config

logger = get_logger()


class Database:
    """Manages SQLite database for papers and extractions."""

    def __init__(self, config: Config):
        """Initialize database with config.

        Args:
            config: Configuration object with database path
        """
        self.config = config
        self.db_path = config.db_path
        self._init_db()

    @contextmanager
    def _get_conn(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database tables."""
        with self._get_conn() as conn:
            # Papers table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,  -- JSON list
                    year INTEGER NOT NULL,
                    abstract TEXT NOT NULL,
                    arxiv_id TEXT,
                    doi TEXT,
                    citation_count INTEGER DEFAULT 0,
                    tldr TEXT,
                    venue TEXT,
                    open_access_pdf_url TEXT,
                    added_at TEXT NOT NULL,
                    UNIQUE(arxiv_id),
                    UNIQUE(doi)
                )
            """)

            # Extractions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT NOT NULL,
                    extraction_type TEXT NOT NULL,
                    content TEXT NOT NULL,  -- JSON
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
                    UNIQUE(paper_id, extraction_type)
                )
            """)

            # Create indices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extractions_paper ON extractions(paper_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extractions_type ON extractions(extraction_type)"
            )

            logger.info("Database initialized", path=str(self.db_path))

    # Paper CRUD operations

    def add_paper(self, paper: Paper) -> bool:
        """Add a paper to the database.

        Args:
            paper: Paper object to add

        Returns:
            True if added successfully, False if already exists
        """
        try:
            with self._get_conn() as conn:
                data = paper.to_dict()
                conn.execute(
                    """
                    INSERT INTO papers (
                        paper_id, title, authors, year, abstract,
                        arxiv_id, doi, citation_count, tldr, venue,
                        open_access_pdf_url, added_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data["paper_id"],
                        data["title"],
                        data["authors"],
                        data["year"],
                        data["abstract"],
                        data["arxiv_id"],
                        data["doi"],
                        data["citation_count"],
                        data["tldr"],
                        data["venue"],
                        data["open_access_pdf_url"],
                        data["added_at"],
                    ),
                )
                logger.info("Paper added", paper_id=paper.paper_id, title=paper.title)
                return True
        except sqlite3.IntegrityError:
            logger.warning("Paper already exists", paper_id=paper.paper_id)
            return False

    def get_paper(self, paper_id: str) -> Paper | None:
        """Get a paper by ID.

        Args:
            paper_id: ID of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM papers WHERE paper_id = ?", (paper_id,)
            ).fetchone()

            if row:
                return Paper.from_dict(dict(row))
            return None

    def list_papers(self, limit: int = 50, offset: int = 0) -> list[Paper]:
        """list all papers in the database.

        Args:
            limit: Maximum number of papers to return
            offset: Number of papers to skip

        Returns:
            list of Paper objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM papers ORDER BY added_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()

            return [Paper.from_dict(dict(row)) for row in rows]

    def count_papers(self) -> int:
        """Get total number of papers in database."""
        with self._get_conn() as conn:
            count = conn.execute("SELECT COUNT(*) FROM papers").fetchone()[0]
            return count

    def search_papers(self, query: str) -> list[Paper]:
        """Search papers by title or abstract.

        Args:
            query: Search query

        Returns:
            list of matching Paper objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM papers 
                WHERE title LIKE ? OR abstract LIKE ?
                ORDER BY citation_count DESC
                LIMIT 20
            """,
                (f"%{query}%", f"%{query}%"),
            ).fetchall()

            return [Paper.from_dict(dict(row)) for row in rows]

    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper and its extractions.

        Args:
            paper_id: ID of the paper to delete

        Returns:
            True if deleted, False if not found
        """
        with self._get_conn() as conn:
            # Delete extractions first (foreign key constraint)
            conn.execute("DELETE FROM extractions WHERE paper_id = ?", (paper_id,))

            # Delete paper
            cursor = conn.execute("DELETE FROM papers WHERE paper_id = ?", (paper_id,))

            if cursor.rowcount > 0:
                logger.info("Paper deleted", paper_id=paper_id)
                return True
            return False

    # Extraction operations

    def add_extraction(self, extraction: Extraction) -> bool:
        """Add or update an extraction.

        Args:
            extraction: Extraction object to add

        Returns:
            True if successful
        """
        with self._get_conn() as conn:
            data = extraction.to_dict()
            conn.execute(
                """
                INSERT OR REPLACE INTO extractions (
                    paper_id, extraction_type, content, created_at
                ) VALUES (?, ?, ?, ?)
            """,
                (
                    data["paper_id"],
                    data["extraction_type"],
                    data["content"],
                    data["created_at"],
                ),
            )
            logger.info(
                "Extraction saved",
                paper_id=extraction.paper_id,
                type=extraction.extraction_type,
            )
            return True

    def get_extraction(self, paper_id: str, extraction_type: str) -> Extraction | None:
        """Get a specific extraction for a paper.

        Args:
            paper_id: ID of the paper
            extraction_type: Type of extraction (e.g., "key_points")

        Returns:
            Extraction object or None if not found
        """
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM extractions 
                WHERE paper_id = ? AND extraction_type = ?
            """,
                (paper_id, extraction_type),
            ).fetchone()

            if row:
                return Extraction.from_dict(dict(row))
            return None

    def list_extractions(self, paper_id: str) -> list[Extraction]:
        """list all extractions for a paper.

        Args:
            paper_id: ID of the paper

        Returns:
            list of Extraction objects
        """
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM extractions WHERE paper_id = ? ORDER BY created_at DESC",
                (paper_id,),
            ).fetchall()

            return [Extraction.from_dict(dict(row)) for row in rows]
