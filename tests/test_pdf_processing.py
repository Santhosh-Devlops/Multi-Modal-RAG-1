import os
import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.pdf_service import PDFService

def test_pdf_extraction():
    sample_pdf = PROJECT_ROOT / "dataset" / "manufacturing" / "industrial_cnc_machining_manual.pdf"
    assert sample_pdf.exists(), "Sample PDF must exist for testing"

    result = PDFService.extract_pdf_content(str(sample_pdf), doc_id=99, doc_domain="Manufacturing")
    assert result["page_count"] >= 15, "PDF should have at least 15 pages"
    assert len(result["pages"]) >= 15, "Extracted pages list should match page count"
    assert len(result["images"]) >= 1, "Should detect at least 1 image/diagram in the manual"
    assert len(result["tables"]) >= 1, "Should detect at least 1 structured table in the manual"
    assert len(result["pages"][0]["page_text"]) > 50, "First page should have non-empty extractable text"
