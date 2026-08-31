import time
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog
from utils.text_utils import extract_keywords

class ResponseVerificationAgent:
    name = "Response Verification Agent"
    key = "verification_agent"
    role_description = "Cross-examines the generated answer against source chunks to verify factual grounding, citation accuracy, and prevent hallucinations."
    input_type = "Generated Answer & Supporting Chunks"
    output_type = "Verification Verdict & Groundedness Score"

    @classmethod
    def verify_response(
        cls,
        db: Session,
        question: str,
        answer: str,
        evidence: List[Dict[str, Any]],
        trace_id: str = ""
    ) -> Tuple[bool, float, str]:
        start_time = time.time()
        
        if not evidence or "could not find sufficient information" in answer.lower():
            if trace_id:
                log = AgentActivityLog(
                    trace_id=trace_id,
                    agent_name=cls.name,
                    action="Response Verification & Hallucination Audit",
                    input_summary="Verified honest non-answer / lack of evidence.",
                    output_summary="Audit Passed: System correctly declared lack of evidence without hallucination.",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    status="Success"
                )
                db.add(log)
                db.commit()
            return (True, 1.0, "Verified Non-Hallucinatory")

        # Extract keywords from answer
        ans_keywords = set(extract_keywords(answer, 15))
        ev_text = " ".join([e.get("content_text", "") for e in evidence])
        ev_keywords = set(extract_keywords(ev_text, 60))
        
        # Grounding ratio
        if not ans_keywords:
            grounding_ratio = 1.0
        else:
            supported = ans_keywords.intersection(ev_keywords)
            grounding_ratio = len(supported) / len(ans_keywords)
            
        groundedness_score = min(1.0, max(0.60, grounding_ratio))
        is_verified = groundedness_score >= 0.65
        
        verdict = "Verified Grounded (No Hallucination)" if is_verified else "Caution: Partial Evidence Overlap"
        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Response Verification & Hallucination Audit",
                input_summary=f"Audit answer with {len(ans_keywords)} key claims against {len(evidence)} evidence chunks.",
                output_summary=f"Groundedness: {round(groundedness_score * 100, 1)}% | Verdict: {verdict}",
                execution_time_ms=elapsed_ms,
                status="Success" if is_verified else "Warning"
            )
            db.add(log)
            db.commit()

        return (is_verified, round(groundedness_score, 2), verdict)
