import sys
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from database import init_db, SessionLocal
from agents.agent_orchestrator import AgentOrchestrator
from agents.query_agent import QueryUnderstandingAgent
from services.vector_store import vector_store
from services.embedding_service import EmbeddingService

def test_query_understanding_agent():
    init_db()
    db = SessionLocal()
    res = QueryUnderstandingAgent.analyze_query(
        db=db,
        question="What is the maximum operating temperature in the specifications table?",
        default_domain="Manufacturing",
        trace_id="test_trace_1"
    )
    assert res["is_numerical"] is True
    assert "Tabular" in res["target_modality"] or "Table" in res["target_modality"]
    assert res["domain"] == "Manufacturing"
    db.close()

def test_multi_agent_pipeline_execution():
    init_db()
    db = SessionLocal()
    AgentOrchestrator.initialize_agent_registry(db)

    # Seed one test vector into the vector store
    sample_text = "Spindle bearing lubrication maintenance interval is every 500 operating hours with ISO VG 46 lubricant."
    vec = EmbeddingService.get_embedding(sample_text)
    vector_store.add_batch([vec], [{
        "chunk_id": 999,
        "document_id": 999,
        "document_name": "cnc_manual.pdf",
        "page_number": 5,
        "content_type": "text",
        "content_text": sample_text,
        "domain": "Manufacturing"
    }])

    res = AgentOrchestrator.execute_multimodal_rag_pipeline(
        db=db,
        question="What is the recommended spindle lubrication maintenance interval?",
        domain="Manufacturing",
        top_k=3
    )

    assert "answer" in res
    assert len(res["answer"]) > 10
    assert "sources" in res
    db.close()
