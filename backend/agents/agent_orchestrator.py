import uuid
import time
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.query_model import QueryRecord, QueryEvidence
from models.agent_model import AgentStatus, AgentActivityLog
from services.nlp_service import NLPService
from agents.query_agent import QueryUnderstandingAgent
from agents.retrieval_agent import RetrievalAgent
from agents.evidence_agent import EvidenceValidationAgent
from agents.answer_agent import RAGAnswerAgent
from agents.verification_agent import ResponseVerificationAgent
from agents.document_agent import DocumentProcessingAgent
from agents.image_agent import ImageUnderstandingAgent
from agents.table_agent import TableUnderstandingAgent

class AgentOrchestrator:
    @staticmethod
    def initialize_agent_registry(db: Session):
        """Seed or update the agents in AgentStatus table."""
        agents = [
            {
                "agent_key": DocumentProcessingAgent.key,
                "agent_name": DocumentProcessingAgent.name,
                "role_description": DocumentProcessingAgent.role_description,
                "input_type": DocumentProcessingAgent.input_type,
                "output_type": DocumentProcessingAgent.output_type,
            },
            {
                "agent_key": ImageUnderstandingAgent.key,
                "agent_name": ImageUnderstandingAgent.name,
                "role_description": ImageUnderstandingAgent.role_description,
                "input_type": ImageUnderstandingAgent.input_type,
                "output_type": ImageUnderstandingAgent.output_type,
            },
            {
                "agent_key": TableUnderstandingAgent.key,
                "agent_name": TableUnderstandingAgent.name,
                "role_description": TableUnderstandingAgent.role_description,
                "input_type": TableUnderstandingAgent.input_type,
                "output_type": TableUnderstandingAgent.output_type,
            },
            {
                "agent_key": QueryUnderstandingAgent.key,
                "agent_name": QueryUnderstandingAgent.name,
                "role_description": QueryUnderstandingAgent.role_description,
                "input_type": QueryUnderstandingAgent.input_type,
                "output_type": QueryUnderstandingAgent.output_type,
            },
            {
                "agent_key": RetrievalAgent.key,
                "agent_name": RetrievalAgent.name,
                "role_description": RetrievalAgent.role_description,
                "input_type": RetrievalAgent.input_type,
                "output_type": RetrievalAgent.output_type,
            },
            {
                "agent_key": EvidenceValidationAgent.key,
                "agent_name": EvidenceValidationAgent.name,
                "role_description": EvidenceValidationAgent.role_description,
                "input_type": EvidenceValidationAgent.input_type,
                "output_type": EvidenceValidationAgent.output_type,
            },
            {
                "agent_key": RAGAnswerAgent.key,
                "agent_name": RAGAnswerAgent.name,
                "role_description": RAGAnswerAgent.role_description,
                "input_type": RAGAnswerAgent.input_type,
                "output_type": RAGAnswerAgent.output_type,
            },
            {
                "agent_key": ResponseVerificationAgent.key,
                "agent_name": ResponseVerificationAgent.name,
                "role_description": ResponseVerificationAgent.role_description,
                "input_type": ResponseVerificationAgent.input_type,
                "output_type": ResponseVerificationAgent.output_type,
            },
        ]
        
        for a_data in agents:
            existing = db.query(AgentStatus).filter(AgentStatus.agent_key == a_data["agent_key"]).first()
            if not existing:
                db_agent = AgentStatus(
                    agent_key=a_data["agent_key"],
                    agent_name=a_data["agent_name"],
                    role_description=a_data["role_description"],
                    input_type=a_data["input_type"],
                    output_type=a_data["output_type"],
                    status="Online"
                )
                db.add(db_agent)
            else:
                existing.status = "Online"
        db.commit()

    @classmethod
    def execute_multimodal_rag_pipeline(
        cls,
        db: Session,
        question: str,
        domain: str = "Manufacturing",
        doc_id: Optional[int] = None,
        top_k: int = 5,
        user_id: Optional[int] = None,
        session_id: str = "default_session",
        chat_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Coordinated Multi-Agent Query Pipeline with NLP & Follow-up Context:
        1. Contextual Query Rewriting (multi-turn follow-ups)
        2. Query Understanding (intent, modality, domain)
        3. 5-Modality Hybrid Retrieval (privacy-isolated by user_id)
        4. Evidence Grounding & Validation
        5. Grounded RAG Synthesis & Citations
        6. Hallucination Audit & Verification
        """
        pipeline_start = time.time()
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"

        # Step 0: NLP Follow-up Query Rewriting
        rewritten_question = NLPService.resolve_followup_context(question, chat_history or [])

        # Step 1: Query Understanding Agent
        query_analysis = QueryUnderstandingAgent.analyze_query(
            db=db,
            question=rewritten_question,
            default_domain=domain,
            trace_id=trace_id
        )
        detected_domain = domain if domain and domain != "All" else query_analysis["domain"]
        target_modality = query_analysis["target_modality"]

        # Step 2: Retrieval Agent (Privacy Isolated)
        raw_evidence = RetrievalAgent.retrieve_evidence(
            db=db,
            question=rewritten_question,
            domain=detected_domain,
            doc_id=doc_id,
            top_k=top_k,
            target_modality=target_modality,
            user_id=user_id,
            trace_id=trace_id
        )

        # Step 3: Evidence Validation Agent
        validated_evidence, evidence_conf, val_status = EvidenceValidationAgent.validate_evidence(
            db=db,
            question=rewritten_question,
            evidence=raw_evidence,
            trace_id=trace_id
        )

        # Step 4: RAG Answer Agent
        answer_text, ans_confidence, citations, ans_status, ext_suggestions = RAGAnswerAgent.generate_answer(
            db=db,
            question=rewritten_question,
            evidence=validated_evidence,
            domain=detected_domain,
            trace_id=trace_id
        )

        # Step 5: Response Verification Agent
        is_verified, groundedness_score, ver_verdict = ResponseVerificationAgent.verify_response(
            db=db,
            question=rewritten_question,
            answer=answer_text,
            evidence=validated_evidence,
            trace_id=trace_id
        )

        total_elapsed_ms = (time.time() - pipeline_start) * 1000

        # Save Query Record in DB
        query_rec = QueryRecord(
            user_id=user_id,
            session_id=session_id,
            question=question,
            intent=query_analysis["intent"],
            domain=detected_domain,
            requested_modality=target_modality,
            answer=answer_text,
            external_suggestions=ext_suggestions,
            confidence_score=ans_confidence,
            groundedness_score=groundedness_score,
            sources_json=json.dumps(citations),
            verification_status=ver_verdict,
            execution_time_ms=total_elapsed_ms
        )
        db.add(query_rec)
        db.flush()

        # Save Evidence Items in DB
        for ev in validated_evidence:
            ev_rec = QueryEvidence(
                query_id=query_rec.id,
                chunk_id=ev.get("chunk_id"),
                document_id=ev.get("document_id", 0),
                document_name=ev.get("document_name", ""),
                page_number=ev.get("page_number", 1),
                content_type=ev.get("content_type", "text"),
                snippet=ev.get("snippet", ""),
                semantic_score=ev.get("semantic_score", 0.0),
                keyword_score=ev.get("keyword_score", 0.0),
                hybrid_score=ev.get("hybrid_score", 0.0),
                is_selected=1
            )
            db.add(ev_rec)

        db.commit()

        return {
            "query_id": query_rec.id,
            "session_id": session_id,
            "trace_id": trace_id,
            "question": question,
            "rewritten_question": rewritten_question if rewritten_question != question else None,
            "intent": query_analysis["intent"],
            "domain": detected_domain,
            "requested_modality": target_modality,
            "answer": answer_text,
            "external_suggestions": ext_suggestions,
            "confidence_score": ans_confidence,
            "groundedness_score": groundedness_score,
            "sources": citations,
            "evidence": validated_evidence,
            "verification_status": ver_verdict,
            "execution_time_ms": round(total_elapsed_ms, 1)
        }
