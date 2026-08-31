import sys
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.chunk_service import ChunkService
from services.table_service import TableService

def test_semantic_chunking():
    pages = [
        {"page_number": 1, "page_text": "This is a detailed paragraph on CNC machining spindle tolerances. " * 30},
        {"page_number": 2, "page_text": "Second page discussing hydraulic fluid pressure limits and cooling circuits. " * 25}
    ]
    chunks = ChunkService.chunk_document_text(pages, doc_id=1, domain="Manufacturing", target_chunk_words=100)
    assert len(chunks) >= 2, "Should create multiple chunks across pages"
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["content_type"] == "text"
    assert chunks[0]["domain"] == "Manufacturing"

def test_table_parsing_and_chunking():
    table_info = {
        "page_number": 3,
        "table_index": 1,
        "raw_markdown": "| Parameter | Normal | Limit |\n| --- | --- | --- |\n| Temp | 50 C | 85 C |",
        "structured_json": [["Parameter", "Normal", "Limit"], ["Temp", "50 C", "85 C"]],
        "natural_language_text": "In table on page 3: Parameter 'Temp' has Normal value '50 C', Limit '85 C'.",
        "row_count": 1,
        "column_count": 3
    }
    t_chunks = TableService.table_to_searchable_chunks(table_info, doc_id=1, domain="Manufacturing")
    assert len(t_chunks) == 1
    assert t_chunks[0]["content_type"] == "table"
    assert "TABLE PAGE 3" in t_chunks[0]["content_text"]
    assert "85 C" in t_chunks[0]["content_text"]
