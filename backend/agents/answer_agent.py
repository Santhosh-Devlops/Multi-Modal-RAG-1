import time
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog
from services.model_service import ModelService

class RAGAnswerAgent:
    name = "RAG Answer Generation Agent"
    key = "answer_agent"
    role_description = "Synthesizes strictly grounded, citation-backed answers in clean markdown using retrieved multimodal context."
    input_type = "Validated Evidence Chunks, User Query"
    output_type = "Grounded Answer, Confidence Score, Source Citations, External Suggestions"

    @classmethod
    def generate_answer(
        cls,
        db: Session,
        question: str,
        evidence: List[Dict[str, Any]],
        domain: str = "Manufacturing",
        trace_id: str = ""
    ) -> Tuple[str, float, List[Dict[str, Any]], str, Optional[str]]:
        start_time = time.time()
        
        answer_text, confidence, citations, status_msg, external_suggestions = ModelService.generate_grounded_answer(
            question=question,
            evidence_list=evidence,
            domain=domain
        )
        
        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Grounded Response Synthesis",
                input_summary=f"Synthesized response using {len(evidence)} evidence sources.",
                output_summary=f"Confidence: {round(confidence * 100, 1)}% | Status: {status_msg}",
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

        return (answer_text, confidence, citations, status_msg, external_suggestions)
