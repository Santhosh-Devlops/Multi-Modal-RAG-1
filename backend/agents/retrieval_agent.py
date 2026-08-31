import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog
from services.retrieval_service import RetrievalService

class RetrievalAgent:
    name = "Retrieval Agent"
    key = "retrieval_agent"
    role_description = "Executes hybrid semantic vector search, BM25 keyword matching, and 5-modality boosting with privacy isolation."
    input_type = "Question, Domain Filter, Modality Target, User ID"
    output_type = "Ranked Evidence Chunks across Text, Images, Graphs, Tables, Numericals"

    @classmethod
    def retrieve_evidence(
        cls,
        db: Session,
        question: str,
        domain: Optional[str] = None,
        doc_id: Optional[int] = None,
        top_k: int = 5,
        target_modality: str = "All",
        user_id: Optional[int] = None,
        trace_id: str = ""
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        
        evidence = RetrievalService.retrieve_hybrid_evidence(
            query=question,
            domain=domain,
            doc_id=doc_id,
            top_k=top_k,
            target_modality=target_modality,
            user_id=user_id
        )
        
        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            summary = f"Retrieved {len(evidence)} chunks (Top Score: {evidence[0]['hybrid_score'] if evidence else 0.0})"
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="5-Modality Hybrid Dense-Sparse Vector Search",
                input_summary=f"Query: '{question}' | Domain: {domain or 'All'} | Top-K: {top_k}",
                output_summary=summary,
                execution_time_ms=elapsed_ms,
                status="Success" if evidence else "Warning"
            )
            db.add(log)
            db.commit()

        return evidence
