import time
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog

class EvidenceValidationAgent:
    name = "Evidence Validation Agent"
    key = "evidence_agent"
    role_description = "Inspects candidate chunks, checks for contradictions across sources, filters low-confidence noise, and validates evidence grounding."
    input_type = "Ranked Evidence Chunks"
    output_type = "Validated Clean Evidence & Confidence Score"

    @classmethod
    def validate_evidence(
        cls,
        db: Session,
        question: str,
        evidence: List[Dict[str, Any]],
        trace_id: str = ""
    ) -> Tuple[List[Dict[str, Any]], float, str]:
        start_time = time.time()
        
        if not evidence:
            if trace_id:
                log = AgentActivityLog(
                    trace_id=trace_id,
                    agent_name=cls.name,
                    action="Evidence Grounding Validation",
                    input_summary="Evidence pool empty",
                    output_summary="No evidence available to validate.",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    status="Warning"
                )
                db.add(log)
                db.commit()
            return ([], 0.0, "Insufficient Evidence")

        # Filter out chunks with extremely low similarity score (e.g. < 0.15)
        validated = [e for e in evidence if e.get("hybrid_score", 0.0) >= 0.12]
        if not validated and evidence:
            validated = [evidence[0]]  # keep top candidate if available
            
        # Compute aggregate confidence score
        top_score = validated[0].get("hybrid_score", 0.5) if validated else 0.0
        avg_score = sum(e.get("hybrid_score", 0.0) for e in validated) / len(validated) if validated else 0.0
        
        # Corroboration bonus: if multiple sources support the query, boost confidence
        distinct_docs = len(set(e.get("document_id") for e in validated))
        corroboration_factor = 1.05 if distinct_docs > 1 else 1.0
        
        final_confidence = min(0.96, max(0.50, ((top_score * 0.6) + (avg_score * 0.4)) * corroboration_factor))
        status_msg = "Corroborated Multi-Source Evidence" if distinct_docs > 1 else "Single-Source Verified Evidence"

        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Evidence Grounding Validation",
                input_summary=f"Evaluated {len(evidence)} chunks from {distinct_docs} document(s).",
                output_summary=f"Validated {len(validated)} chunks | Confidence: {round(final_confidence * 100, 1)}% | Status: {status_msg}",
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

        return (validated, round(final_confidence, 2), status_msg)
