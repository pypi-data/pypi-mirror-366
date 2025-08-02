"""Tests for PDF processing functionality."""


import pytest

from litai.config import Config
from litai.database import Database
from litai.models import Paper
from litai.pdf_processor import PDFProcessor


@pytest.fixture
def pdf_processor(tmp_path):
    """Create a PDFProcessor instance with test database."""
    config = Config(base_dir=tmp_path)
    db = Database(config)
    processor = PDFProcessor(db, tmp_path)

    # Add a test paper with real arxiv URL
    test_paper = Paper(
        paper_id="test123",
        title="Attention Is All You Need",
        authors=["Vaswani", "Shazeer"],
        year=2017,
        abstract="The dominant sequence transduction models...",
        arxiv_id="1706.03762",
        open_access_pdf_url="https://arxiv.org/abs/1706.03762",
    )
    db.add_paper(test_paper)

    return processor, db


@pytest.mark.asyncio
async def test_pdf_directory_creation(tmp_path):
    """Test that PDF directory is created on initialization."""
    config = Config(base_dir=tmp_path)
    db = Database(config)

    PDFProcessor(db, tmp_path)  # initializing creates the pdfs directory
    assert (tmp_path / "pdfs").exists()
    assert (tmp_path / "pdfs").is_dir()


@pytest.mark.asyncio
async def test_get_pdf_path(pdf_processor):
    """Test PDF path generation."""
    processor, _ = pdf_processor
    path = processor._get_pdf_path("test123")
    assert path.name == "test123.pdf"
    assert "pdfs" in str(path)


@pytest.mark.asyncio
async def test_process_paper_not_found(pdf_processor):
    """Test processing a paper that doesn't exist."""
    processor, _ = pdf_processor
    result = await processor.process_paper("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_download_pdf_already_exists(pdf_processor):
    """Test that existing PDFs are not re-downloaded."""
    processor, db = pdf_processor

    # Create existing PDF
    paper = db.get_paper("test123")
    pdf_path = processor._get_pdf_path(paper.paper_id)
    pdf_path.parent.mkdir(exist_ok=True)
    pdf_path.write_text("existing pdf content")

    # Try to download
    result = await processor.download_pdf(paper)
    assert result == pdf_path
    assert pdf_path.read_text() == "existing pdf content"  # Not overwritten


@pytest.mark.asyncio
async def test_extract_text_invalid_pdf(pdf_processor, tmp_path):
    """Test handling of invalid PDF files."""
    processor, _ = pdf_processor

    # Create invalid PDF
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_text("This is not a valid PDF")

    # Should raise exception
    with pytest.raises(Exception):
        processor.extract_text(bad_pdf)
