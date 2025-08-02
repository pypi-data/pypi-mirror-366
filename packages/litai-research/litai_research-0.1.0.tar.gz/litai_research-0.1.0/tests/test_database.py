"""Tests for database operations."""

import pytest
from pathlib import Path
import tempfile
import shutil

from litai.config import Config
from litai.database import Database
from litai.models import Paper, Extraction


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test config with temporary directory."""
    return Config(base_dir=temp_dir)


@pytest.fixture
def db(config):
    """Create a test database."""
    return Database(config)


@pytest.fixture
def sample_paper():
    """Create a sample paper for testing."""
    return Paper(
        paper_id="test123",
        title="Test Paper: A Study of Testing",
        authors=["John Doe", "Jane Smith"],
        year=2024,
        abstract="This is a test abstract about testing things.",
        arxiv_id="2401.12345",
        doi="10.1234/test.2024",
        citation_count=42,
        tldr="Testing is important",
        venue="Test Conference 2024",
        open_access_pdf_url="https://arxiv.org/pdf/2401.12345.pdf"
    )


class TestDatabase:
    """Test database operations."""
    
    def test_init_creates_tables(self, db, config):
        """Test that database initialization creates required tables."""
        # Check that database file exists
        assert config.db_path.exists()
        
        # Check tables exist
        with db._get_conn() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [row[0] for row in tables]
            
            assert "papers" in table_names
            assert "extractions" in table_names
    
    def test_add_paper(self, db, sample_paper):
        """Test adding a paper to the database."""
        # Add paper
        assert db.add_paper(sample_paper) is True
        
        # Try to add same paper again
        assert db.add_paper(sample_paper) is False
    
    def test_get_paper(self, db, sample_paper):
        """Test retrieving a paper by ID."""
        # Add paper
        db.add_paper(sample_paper)
        
        # Retrieve paper
        retrieved = db.get_paper(sample_paper.paper_id)
        assert retrieved is not None
        assert retrieved.title == sample_paper.title
        assert retrieved.authors == sample_paper.authors
        assert retrieved.year == sample_paper.year
        
        # Try to retrieve non-existent paper
        assert db.get_paper("nonexistent") is None
    
    def test_list_papers(self, db):
        """Test listing papers."""
        # Add multiple papers
        for i in range(5):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2020 + i,
                abstract=f"Abstract {i}"
            )
            db.add_paper(paper)
        
        # List all papers
        papers = db.list_papers()
        assert len(papers) == 5
        
        # Test pagination
        papers = db.list_papers(limit=2)
        assert len(papers) == 2
        
        papers = db.list_papers(limit=2, offset=2)
        assert len(papers) == 2
    
    def test_count_papers(self, db):
        """Test counting papers."""
        assert db.count_papers() == 0
        
        # Add papers
        for i in range(3):
            paper = Paper(
                paper_id=f"test{i}",
                title=f"Test Paper {i}",
                authors=[f"Author {i}"],
                year=2024,
                abstract=f"Abstract {i}"
            )
            db.add_paper(paper)
        
        assert db.count_papers() == 3
    
    def test_search_papers(self, db):
        """Test searching papers."""
        # Add papers with different content
        papers = [
            Paper(
                paper_id="ml1",
                title="Machine Learning Fundamentals",
                authors=["ML Author"],
                year=2024,
                abstract="This paper covers machine learning basics."
            ),
            Paper(
                paper_id="dl1",
                title="Deep Learning Advanced Topics",
                authors=["DL Author"],
                year=2024,
                abstract="Advanced deep learning techniques."
            ),
            Paper(
                paper_id="nlp1",
                title="Natural Language Processing",
                authors=["NLP Author"],
                year=2024,
                abstract="NLP with machine learning approaches."
            ),
        ]
        
        for paper in papers:
            db.add_paper(paper)
        
        # Search by title
        results = db.search_papers("machine learning")
        assert len(results) == 2  # Found in ML paper title and NLP abstract
        paper_ids = [r.paper_id for r in results]
        assert "ml1" in paper_ids
        assert "nlp1" in paper_ids
        
        # Search by abstract
        results = db.search_papers("learning")
        assert len(results) == 3  # All papers mention learning
    
    def test_delete_paper(self, db, sample_paper):
        """Test deleting a paper."""
        # Add paper
        db.add_paper(sample_paper)
        assert db.get_paper(sample_paper.paper_id) is not None
        
        # Delete paper
        assert db.delete_paper(sample_paper.paper_id) is True
        assert db.get_paper(sample_paper.paper_id) is None
        
        # Try to delete non-existent paper
        assert db.delete_paper("nonexistent") is False
    
    def test_add_extraction(self, db, sample_paper):
        """Test adding an extraction."""
        # Add paper first
        db.add_paper(sample_paper)
        
        # Create extraction
        extraction = Extraction(
            paper_id=sample_paper.paper_id,
            extraction_type="key_points",
            content={
                "points": [
                    {"claim": "Testing is important", "evidence": "Section 1"},
                    {"claim": "Tests prevent bugs", "evidence": "Section 2"}
                ]
            }
        )
        
        assert db.add_extraction(extraction) is True
    
    def test_get_extraction(self, db, sample_paper):
        """Test retrieving an extraction."""
        # Add paper and extraction
        db.add_paper(sample_paper)
        
        extraction = Extraction(
            paper_id=sample_paper.paper_id,
            extraction_type="key_points",
            content={"points": ["point1", "point2"]}
        )
        db.add_extraction(extraction)
        
        # Retrieve extraction
        retrieved = db.get_extraction(sample_paper.paper_id, "key_points")
        assert retrieved is not None
        assert retrieved.extraction_type == "key_points"
        assert retrieved.content == {"points": ["point1", "point2"]}
        
        # Try to retrieve non-existent extraction
        assert db.get_extraction(sample_paper.paper_id, "nonexistent") is None
    
    def test_list_extractions(self, db, sample_paper):
        """Test listing extractions for a paper."""
        # Add paper
        db.add_paper(sample_paper)
        
        # Add multiple extractions
        extraction_types = ["key_points", "methodology", "results"]
        for ext_type in extraction_types:
            extraction = Extraction(
                paper_id=sample_paper.paper_id,
                extraction_type=ext_type,
                content={ext_type: f"content for {ext_type}"}
            )
            db.add_extraction(extraction)
        
        # List extractions
        extractions = db.list_extractions(sample_paper.paper_id)
        assert len(extractions) == 3
        
        # Verify all types are present
        types = [e.extraction_type for e in extractions]
        assert set(types) == set(extraction_types)
    
    def test_delete_paper_cascades_extractions(self, db, sample_paper):
        """Test that deleting a paper also deletes its extractions."""
        # Add paper and extraction
        db.add_paper(sample_paper)
        
        extraction = Extraction(
            paper_id=sample_paper.paper_id,
            extraction_type="key_points",
            content={"test": "data"}
        )
        db.add_extraction(extraction)
        
        # Verify extraction exists
        assert db.get_extraction(sample_paper.paper_id, "key_points") is not None
        
        # Delete paper
        db.delete_paper(sample_paper.paper_id)
        
        # Verify extraction is also deleted
        assert db.get_extraction(sample_paper.paper_id, "key_points") is None