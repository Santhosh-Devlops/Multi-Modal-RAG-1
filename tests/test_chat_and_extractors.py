import pytest
from database import SessionLocal, init_db
from models.user_model import User
from models.document_model import (
    Document,
    DocumentPage,
    DocumentChunk,
    DocumentImage,
    DocumentGraph,
    DocumentTable,
    DocumentNumerical
)
from agents.document_agent import DocumentProcessingAgent
from agents.agent_orchestrator import AgentOrchestrator
from services.nlp_service import NLPService
from services.vector_store import vector_store

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    AgentOrchestrator.initialize_agent_registry(db)
    yield db
    db.close()

def test_nlp_query_service():
    query = "What is the maximum operating temperature and hydraulic pressure?"
    res = NLPService.extract_keywords_and_phrases(query)
    assert len(res["keywords"]) > 0
    assert len(res["tokens"]) > 0

    # Test follow-up resolution
    history = [
        {"sender": "user", "text": "What is the maximum operating temperature?"},
        {"sender": "assistant", "text": "The maximum operating temperature is 85°C."}
    ]
    rewritten = NLPService.resolve_followup_context("What about the hydraulic pressure?", history)
    assert "hydraulic pressure" in rewritten.lower()
    assert "temperature" in rewritten.lower()

def test_5_specialized_extractors_ingestion(db_session):
    sample_pdf = "dataset/manufacturing/industrial_cnc_machining_manual.pdf"
    
    doc = Document(
        user_id=1,
        filename="cnc_test_manual.pdf",
        file_path=sample_pdf,
        file_type="pdf",
        file_size=10000,
        domain="Manufacturing",
        doc_type="Technical Manual",
        status="Pending"
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    res = DocumentProcessingAgent.process_document(db_session, doc.id, "trace_test_5_extractors")
    assert res["status"] == "success"
    assert doc.status == "Completed"
    assert doc.page_count > 0
    assert doc.table_count > 0
    assert doc.numerical_count > 0

    # Verify extracted records in DB
    pages = db_session.query(DocumentPage).filter(DocumentPage.document_id == doc.id).all()
    assert len(pages) > 0

    tables = db_session.query(DocumentTable).filter(DocumentTable.document_id == doc.id).all()
    assert len(tables) > 0

    numericals = db_session.query(DocumentNumerical).filter(DocumentNumerical.document_id == doc.id).all()
    assert len(numericals) > 0

def test_multimodal_rag_chat_answering(db_session):
    # Test numerical query
    ans = AgentOrchestrator.execute_multimodal_rag_pipeline(
        db=db_session,
        question="What is the critical shutdown operating temperature?",
        domain="Manufacturing",
        user_id=1,
        session_id="test_session_1"
    )
    assert ans["answer"] is not None
    assert len(ans["sources"]) > 0
    assert ans["verification_status"] is not None

    # Test summary query
    summary_ans = AgentOrchestrator.execute_multimodal_rag_pipeline(
        db=db_session,
        question="Summarize this technical manual",
        domain="Manufacturing",
        user_id=1,
        session_id="test_session_1"
    )
    assert "Summary" in summary_ans["answer"] or "summary" in summary_ans["answer"].lower()
