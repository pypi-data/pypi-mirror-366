"""Tests for configuration management."""

import pytest
from pathlib import Path
import tempfile
import shutil

from litai.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestConfig:
    """Test configuration management."""
    
    def test_default_base_dir(self):
        """Test that default base directory is ~/.litai."""
        config = Config()
        assert config.base_dir == Path.home() / ".litai"
    
    def test_custom_base_dir(self, temp_dir):
        """Test using a custom base directory."""
        config = Config(base_dir=temp_dir)
        assert config.base_dir == temp_dir
    
    def test_directories_created(self, temp_dir):
        """Test that all required directories are created."""
        config = Config(base_dir=temp_dir)
        
        # Check all directories exist
        assert config.base_dir.exists()
        assert config.pdfs_dir.exists()
        assert config.db_dir.exists()
        
        # Check they are directories
        assert config.base_dir.is_dir()
        assert config.pdfs_dir.is_dir()
        assert config.db_dir.is_dir()
    
    def test_pdfs_dir_path(self, temp_dir):
        """Test PDFs directory path."""
        config = Config(base_dir=temp_dir)
        assert config.pdfs_dir == temp_dir / "pdfs"
    
    def test_db_dir_path(self, temp_dir):
        """Test database directory path."""
        config = Config(base_dir=temp_dir)
        assert config.db_dir == temp_dir / "db"
    
    def test_db_path(self, temp_dir):
        """Test database file path."""
        config = Config(base_dir=temp_dir)
        assert config.db_path == temp_dir / "db" / "litai.db"
    
    def test_pdf_path(self, temp_dir):
        """Test PDF path generation."""
        config = Config(base_dir=temp_dir)
        
        paper_id = "test123"
        pdf_path = config.pdf_path(paper_id)
        
        assert pdf_path == temp_dir / "pdfs" / "test123.pdf"
        assert pdf_path.parent.exists()  # Directory should exist