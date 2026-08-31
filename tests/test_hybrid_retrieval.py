import sys
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from services.retrieval_service import RetrievalService

def test_embedding_generation():
    text = "Hydraulic pressure relief valve operating at 160 bar."
    vec = EmbeddingService.get_embedding(text)
    assert len(vec) == 384, "Embedding should have 384 dimensions"
    assert sum(vec) != 0.0, "Embedding should be non-zero"

def test_vector_store_and_hybrid_search():
    store = VectorStore()
    store.clear()

    # Add sample chunks
    c1 = "Spindle bearing high speed lubrication protocol every 500 operating hours."
    c2 = "MRI superconducting cryogen liquid helium boil-off pressure limit 1.25 bar."
    
    v1 = EmbeddingService.get_embedding(c1)
    v2 = EmbeddingService.get_embedding(c2)

    store.add_batch([v1, v2], [
        {"chunk_id": 1, "document_id": 10, "document_name": "cnc.pdf", "page_number": 5, "content_type": "text", "content_text": c1, "domain": "Manufacturing"},
        {"chunk_id": 2, "document_id": 20, "document_name": "mri.pdf", "page_number": 6, "content_type": "text", "content_text": c2, "domain": "Healthcare"}
    ])

    # Search with Manufacturing query
    query = "How often should spindle bearings be lubricated?"
    q_vec = EmbeddingService.get_embedding(query)
    results = store.search(q_vec, top_k=2)
    assert len(results) == 2
    assert results[0]["chunk_id"] == 1, "CNC chunk should rank highest for spindle question"

    # Test domain filter
    hc_results = store.search(q_vec, top_k=2, domain_filter="Healthcare")
    assert len(hc_results) == 1
    assert hc_results[0]["domain"] == "Healthcare"
