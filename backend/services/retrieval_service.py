import re
from typing import List, Dict, Any, Optional
from services.vector_store import vector_store
from services.embedding_service import EmbeddingService
from services.nlp_service import NLPService
from utils.text_utils import extract_keywords, highlight_snippets
from config import HYBRID_SEMANTIC_WEIGHT, HYBRID_KEYWORD_WEIGHT

class RetrievalService:
    @staticmethod
    def calculate_keyword_score(query: str, text: str) -> float:
        """
        Calculate BM25-inspired term overlap score between query keywords and text snippet.
        """
        if not text:
            return 0.0
            
        nlp_res = NLPService.extract_keywords_and_phrases(query)
        primary_words = extract_keywords(query, max_keywords=8)
        phrases = nlp_res["phrases"]
        expanded_keywords = nlp_res["keywords"]
        
        if not primary_words:
            return 0.5
            
        text_lower = text.lower()
        matched = 0.0
        total_weight = 0.0
        
        # Check phrase matches (high weight)
        for phrase in phrases:
            if phrase in text_lower:
                matched += 1.5
        
        # Base weight calculated on primary query tokens only
        for idx, w in enumerate(primary_words):
            importance = 1.0 / (1.0 + 0.15 * idx)
            total_weight += importance
            
            pattern = rf"\b{re.escape(w)}\b"
            if re.search(pattern, text_lower):
                matched += (importance * 1.2)
            elif w in text_lower:
                matched += (importance * 0.7)

        # Bonus for semantic expansions
        for exp_w in expanded_keywords:
            if exp_w not in primary_words and exp_w in text_lower:
                matched += 0.3
                
        raw_score = matched / total_weight if total_weight > 0 else 0.0
        return min(1.0, max(0.0, raw_score))

    @classmethod
    def retrieve_hybrid_evidence(
        cls,
        query: str,
        domain: Optional[str] = None,
        doc_id: Optional[int] = None,
        top_k: int = 5,
        target_modality: str = "All",
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Hybrid dense-sparse retrieval across 5 modalities:
        1. Summarization query handling
        2. Semantic dense search (filtered by user_id for privacy)
        3. Sparse BM25 / NLP keyword and phrase matching
        4. 5-Modality boost (Text, Image, Graph, Table, Numerical)
        """
        q_lower = query.lower().strip()
        is_summary_query = any(k in q_lower for k in [
            "summarize", "summary", "overview", "what is this", "explain this document", "describe this manual", "outline"
        ])

        # Summary / Overview retrieval
        if is_summary_query and len(vector_store.metadata) > 0:
            summary_candidates = []
            for meta in vector_store.metadata:
                if user_id is not None and meta.get("user_id") is not None and meta.get("user_id") != user_id:
                    continue
                if doc_id is not None and meta.get("document_id") != doc_id:
                    continue
                p_num = meta.get("page_number", 1)
                c_type = meta.get("content_type", "text")
                
                # Prioritize early page text chunks for high-level summary
                weight = 0.98 if p_num == 1 else (0.92 if p_num == 2 else 0.85)
                if c_type == "text":
                    weight += 0.05
                elif c_type == "table":
                    weight -= 0.05
                elif c_type == "numerical":
                    weight -= 0.10
                    
                cand = dict(meta)
                cand["semantic_score"] = round(weight, 4)
                cand["keyword_score"] = 0.85
                cand["hybrid_score"] = round(weight, 4)
                cand["snippet"] = cand.get("content_text", "")[:350]
                summary_candidates.append(cand)
                
            summary_candidates.sort(key=lambda x: -x.get("hybrid_score", 0))
            if summary_candidates:
                return summary_candidates[:max(top_k, 6)]

        # Standard Hybrid Retrieval
        query_vec = EmbeddingService.get_embedding(query)
        candidates = vector_store.search(
            query_vector=query_vec,
            top_k=max(20, top_k * 4),
            domain_filter=domain,
            doc_id_filter=doc_id,
            user_id_filter=user_id
        )
        
        # Fallback 1: If filtered search was empty, try broader doc_id search
        if not candidates and doc_id is not None:
            candidates = vector_store.search(
                query_vector=query_vec,
                top_k=max(20, top_k * 4),
                domain_filter=None,
                doc_id_filter=doc_id,
                user_id_filter=None
            )

        # Fallback 2: Direct database chunks retrieval if vector store is sparse
        if not candidates and doc_id is not None:
            try:
                from database import SessionLocal
                from models.document_model import Document, DocumentChunk
                db_s = SessionLocal()
                doc_record = db_s.query(Document).filter(Document.id == doc_id).first()
                chunks = db_s.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()
                if not chunks and doc_record:
                    # Create a synthetic metadata block for count / metadata questions
                    candidates = [{
                        "document_id": doc_record.id,
                        "document_name": doc_record.filename,
                        "content_text": f"Document {doc_record.filename} with {doc_record.page_count} pages, {doc_record.image_count} images, {doc_record.table_count} tables, {doc_record.graph_count} graphs.",
                        "content_type": "text",
                        "page_number": 1,
                        "semantic_score": 0.85
                    }]
                else:
                    for chk in chunks[:top_k * 4]:
                        candidates.append({
                            "document_id": chk.document_id,
                            "document_name": doc_record.filename if doc_record else f"Doc #{doc_id}",
                            "content_text": chk.content_text,
                            "content_type": chk.content_type or "text",
                            "page_number": chk.page_number or 1,
                            "semantic_score": 0.80
                        })
                db_s.close()
            except Exception:
                pass
        
        if not candidates:
            # Fallback 3: Return any available doc metadata if user asks general document questions
            nlp_intent = NLPService.detect_user_intent(query)
            if nlp_intent in ["IMAGE_COUNT", "TABLE_COUNT", "PAGE_COUNT", "EQUATION_COUNT", "SUMMARY"]:
                try:
                    from database import SessionLocal
                    from models.document_model import Document
                    db_s = SessionLocal()
                    doc_query = db_s.query(Document)
                    if user_id:
                        doc_query = doc_query.filter(Document.user_id == user_id)
                    latest_doc = doc_query.order_by(Document.created_at.desc()).first()
                    if latest_doc:
                        candidates = [{
                            "document_id": latest_doc.id,
                            "document_name": latest_doc.filename,
                            "content_text": f"Document {latest_doc.filename} with {latest_doc.page_count} pages, {latest_doc.image_count} images, {latest_doc.table_count} tables.",
                            "content_type": "text",
                            "page_number": 1,
                            "semantic_score": 0.90
                        }]
                    db_s.close()
                except Exception:
                    pass

        if not candidates:
            return []
            
        ranked_evidence = []
        for cand in candidates:
            chunk_text = cand.get("content_text", "")
            sem_score = cand.get("semantic_score", 0.5)
            kw_score = cls.calculate_keyword_score(query, chunk_text)
            
            # Modality boost across 5 modalities
            modality_boost = 1.0
            content_type = cand.get("content_type", "text")
            
            # Numerical / measurement query -> boost numerical and table chunks
            if any(w in q_lower for w in ["value", "limit", "measurement", "temperature", "pressure", "speed", "rpm", "bar", "tolerance", "hours", "formula", "equation", "shutdown", "threshold"]):
                if content_type in ["numerical", "table"]:
                    modality_boost = 1.35
            # Table query -> boost table chunks
            elif any(w in q_lower for w in ["table", "matrix", "column", "row", "specification", "rating"]) and content_type == "table":
                modality_boost = 1.30
            # Graph / chart query -> boost graph chunks
            elif any(w in q_lower for w in ["graph", "chart", "trend", "flowchart", "workflow", "schematic", "architecture", "curve"]) and content_type == "graph":
                modality_boost = 1.30
            # Image query -> boost image chunks
            elif any(w in q_lower for w in ["image", "photo", "drawing", "figure", "picture"]) and content_type == "image":
                modality_boost = 1.25
                
            hybrid_score = ((HYBRID_SEMANTIC_WEIGHT * sem_score) + (HYBRID_KEYWORD_WEIGHT * kw_score)) * modality_boost
            hybrid_score = min(1.0, max(0.0, hybrid_score))
            
            snippet = highlight_snippets(chunk_text, query, max_chars=350)
            
            cand_copy = dict(cand)
            cand_copy["semantic_score"] = round(sem_score, 4)
            cand_copy["keyword_score"] = round(kw_score, 4)
            cand_copy["hybrid_score"] = round(hybrid_score, 4)
            cand_copy["snippet"] = snippet
            ranked_evidence.append(cand_copy)
            
        ranked_evidence.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return ranked_evidence[:top_k]
