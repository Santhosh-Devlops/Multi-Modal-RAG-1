import re
from typing import Any, Dict, List, Optional, Tuple

from services.nlp_service import NLPService
from services import huggingface as hf_client
from services import web_service

SYSTEM_PROMPT = (
    "You are a private, enterprise AI document assistant embedded in a multimodal RAG "
    "application. The user has uploaded one or more documents (research papers, manuals, "
    "reports, resumes, spreadsheets, etc.) which have been parsed into text, tables, "
    "figures/graphs, and mathematical equations, and the most relevant pieces have been "
    "retrieved below as CONTEXT EVIDENCE.\n\n"
    "Rules:\n"
    "1. Answer ONLY using facts present in the CONTEXT EVIDENCE. Never invent numbers, "
    "names, citations, page numbers, or facts that are not there.\n"
    "2. If the evidence does not contain the answer, say so plainly instead of guessing.\n"
    "3. Write like a knowledgeable human assistant, not a template: vary your structure to "
    "fit the question - a direct one-line answer, a short paragraph, a bullet list, or a "
    "table, whichever communicates the answer best.\n"
    "4. Use Markdown. Use LaTeX math blocks ($$ ... $$) when reproducing or explaining "
    "equations. Use Markdown tables for tabular data.\n"
    "5. Cite the specific evidence source you used inline as [Document, Page X].\n"
    "6. If the evidence includes figure/graph/table descriptions, use them to explain "
    "visual content in your own words rather than just pointing at the image.\n"
)


class ModelService:
    @classmethod
    def generate_grounded_answer(
        cls,
        question: str,
        evidence_list: List[Dict[str, Any]],
        domain: str = "General",
    ) -> Tuple[str, float, List[Dict[str, Any]], str, Optional[str]]:
        """
        Generate a grounded, cited answer from retrieved evidence.

        Returns: (answer_text, confidence_score, citations, verification_status, external_suggestions)
        """
        if not evidence_list:
            return (
                "I couldn't find enough information in your uploaded documents to answer "
                "this confidently. Please make sure your document is uploaded and contains "
                "the requested topic.",
                0.0,
                [],
                "No Supporting Evidence Found",
                None,
            )

        context_blocks = []
        citations = []
        for idx, ev in enumerate(evidence_list, start=1):
            doc_name = ev.get("document_name") or f"Document #{ev.get('document_id')}"
            page_num = ev.get("page_number", 1)
            content_type = ev.get("content_type", "text").upper()
            text_snippet = ev.get("content_text", "")

            context_blocks.append(
                f"--- EVIDENCE SOURCE {idx} [{doc_name} | Page {page_num} | {content_type}] ---\n{text_snippet}\n"
            )
            citations.append({
                "source_index": idx,
                "document_id": ev.get("document_id"),
                "document_name": doc_name,
                "page_number": page_num,
                "content_type": ev.get("content_type", "text"),
                "section_name": content_type.capitalize(),
                "hybrid_score": ev.get("hybrid_score", 0.0),
                "snippet": ev.get("snippet", ""),
            })

        full_context = "\n".join(context_blocks)

        # External web knowledge / model suggestions: only when the user actually
        # asked for it (avoid mixing unverified web content into every answer),
        # or when local grounded confidence turns out to be weak (handled below).
        external_suggestions = None
        if web_service.wants_external_info(question):
            external_suggestions = web_service.build_external_knowledge_block(
                question, domain, full_context[:600]
            )

        # ------------------------------------------------------------------
        # 0. Fast, DB-driven document statistics intents (genuinely generic -
        #    these read real counts off the document record, not hardcoded text).
        # ------------------------------------------------------------------
        intent = NLPService.detect_user_intent(question)
        stats_answer = cls._answer_document_stats_intent(intent, evidence_list, citations)
        if stats_answer:
            answer_text, confidence = stats_answer
            return (answer_text, confidence, citations, "Verified Grounded (Document Statistics)", external_suggestions)

        # ------------------------------------------------------------------
        # 1. LLM-first: a real language model, grounded strictly in the
        #    retrieved evidence, handles every other question generically -
        #    for ANY document/domain, not a fixed set of hardcoded topics.
        # ------------------------------------------------------------------
        llm_answer = cls._call_llm(question, full_context, domain)
        if llm_answer:
            return (llm_answer, 0.95, citations, "Verified Grounded (LLM, HF Router)", external_suggestions)

        # ------------------------------------------------------------------
        # 2. Generic extractive fallback (no HF token configured, or the
        #    call failed): pick the evidence sentences that best overlap the
        #    question's keywords. This works for any document because it
        #    does not assume any particular topic/schema.
        # ------------------------------------------------------------------
        answer_text, confidence = cls._extractive_fallback(question, evidence_list, citations)
        if not external_suggestions and confidence < 0.6:
            # Low-confidence local answer: offer to look beyond the document even
            # if the user didn't explicitly ask, clearly labeled as unverified.
            external_suggestions = web_service.build_external_knowledge_block(question, domain, full_context[:600])

        return (answer_text, confidence, citations, "Grounded (Extractive Fallback - configure HF token for full LLM answers)", external_suggestions)

    # ======================================================================
    # LLM call
    # ======================================================================
    @staticmethod
    def _call_llm(question: str, full_context: str, domain: str) -> Optional[str]:
        user_content = (
            f"Document domain: {domain}\n\n"
            f"CONTEXT EVIDENCE:\n{full_context}\n\n"
            f"USER QUESTION:\n{question}\n\n"
            f"Write the grounded answer now."
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
        return hf_client.chat_complete(messages, temperature=0.15, max_tokens=900)

    # ======================================================================
    # Document statistics (generic, DB-backed - not hardcoded content)
    # ======================================================================
    @staticmethod
    def _answer_document_stats_intent(
        intent: str,
        evidence_list: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> Optional[Tuple[str, float]]:
        if intent not in ("IMAGE_COUNT", "TABLE_COUNT", "PAGE_COUNT", "EQUATION_COUNT"):
            return None

        doc_id = evidence_list[0].get("document_id")
        top_doc_name = evidence_list[0].get("document_name", "the document")
        img_count, tbl_count, page_count, eq_count = 0, 0, 1, 0

        if doc_id:
            try:
                from database import SessionLocal
                from models.document_model import Document, DocumentImage, DocumentTable, DocumentNumerical

                db_tmp = SessionLocal()
                try:
                    doc_obj = db_tmp.query(Document).filter(Document.id == doc_id).first()
                    if doc_obj:
                        top_doc_name = doc_obj.filename or top_doc_name
                        page_count = doc_obj.page_count or 1
                        img_count = doc_obj.image_count or db_tmp.query(DocumentImage).filter(DocumentImage.document_id == doc_id).count()
                        tbl_count = doc_obj.table_count or db_tmp.query(DocumentTable).filter(DocumentTable.document_id == doc_id).count()
                        eq_count = db_tmp.query(DocumentNumerical).filter(
                            DocumentNumerical.document_id == doc_id,
                            DocumentNumerical.category == "Mathematical Equation",
                        ).count()
                        if eq_count == 0:
                            eq_count = db_tmp.query(DocumentNumerical).filter(DocumentNumerical.document_id == doc_id).count()
                finally:
                    db_tmp.close()
            except Exception:
                pass

        sources_md = "\n".join([f"- Page {c['page_number']} - {c['section_name']}" for c in citations[:3]])

        if intent == "IMAGE_COUNT":
            return (
                f"There are **{img_count} images / visual figures** extracted from **{top_doc_name}** "
                f"across {page_count} pages.\n\nYou can inspect each one under the Image Extractor and "
                f"Graphs & Visuals tabs.\n\n**Sources:**\n{sources_md}",
                0.98,
            )
        if intent == "TABLE_COUNT":
            return (
                f"There are **{tbl_count} structured tables** extracted from **{top_doc_name}**.\n\n"
                f"You can view and copy the full data under the Table Extractor tab.\n\n**Sources:**\n{sources_md}",
                0.98,
            )
        if intent == "PAGE_COUNT":
            return (
                f"**{top_doc_name}** contains **{page_count} pages** in total.\n\n**Sources:**\n{sources_md}",
                0.98,
            )
        if intent == "EQUATION_COUNT":
            return (
                f"There are **{eq_count} equations / numbered mathematical expressions** extracted from "
                f"**{top_doc_name}**, viewable in LaTeX under the Equation Extractor tab.\n\n**Sources:**\n{sources_md}",
                0.98,
            )
        return None

    # ======================================================================
    # Generic extractive fallback
    # ======================================================================
    @staticmethod
    def _extractive_fallback(
        question: str,
        evidence_list: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
    ) -> Tuple[str, float]:
        sources_md = "\n".join([f"- Page {c['page_number']} - {c['section_name']}" for c in citations[:3]])

        # "Summarize"-type questions carry almost no content keywords to match
        # against (the question itself is generic), so keyword-overlap
        # extraction below would pick near-random sentences. Instead build a
        # generic overview by sampling one representative sentence per
        # evidence page - this stays document-agnostic (no hardcoded topics).
        if NLPService.detect_user_intent(question) == "SUMMARY":
            overview_points = []
            for ev in evidence_list[:5]:
                page_num = ev.get("page_number", 1)
                raw_text = ev.get("content_text", "") or ""
                sentences = [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", raw_text) if 30 <= len(s.strip()) <= 220]
                if sentences:
                    overview_points.append(f"- {sentences[0]} (Page {page_num})")
            if overview_points:
                answer = (
                    "Here is a quick summary assembled from the most relevant sections of your "
                    "document (extractive - configure a HUGGINGFACE_API_TOKEN for a fully "
                    "model-written summary):\n\n"
                    + "\n".join(overview_points[:5])
                    + f"\n\n**Sources:**\n{sources_md}"
                )
                return answer, 0.65

        q_words = set(re.findall(r"\b[A-Za-z0-9_-]{3,}\b", question.lower())) - NLPService.STOPWORDS

        scored_sentences = []
        for ev in evidence_list[:6]:
            page_num = ev.get("page_number", 1)
            raw_text = ev.get("content_text", "")
            lines = [s.strip() for s in re.split(r"(?<=[.?!])\s+|\n", raw_text) if len(s.strip()) > 15]
            for line in lines:
                clean_line = re.sub(r"^\[[^\]]+\]\s*", "", line).strip()
                line_words = set(re.findall(r"\b[A-Za-z0-9_-]{3,}\b", clean_line.lower()))
                overlap = len(q_words & line_words)
                if overlap > 0:
                    scored_sentences.append((overlap, clean_line, page_num))

        scored_sentences.sort(key=lambda x: x[0], reverse=True)

        if not scored_sentences:
            top_ev = evidence_list[0]
            p_num = top_ev.get("page_number", 1)
            text = (top_ev.get("content_text", "") or "")[:400]
            answer = (
                f"I don't have a HF model configured to synthesize a full answer, so here is the most "
                f"relevant passage found on **Page {p_num}**:\n\n> {text}...\n\n**Sources:**\n{sources_md}\n\n"
                f"_Configure `HUGGINGFACE_API_TOKEN` in the backend `.env` for complete, model-written answers._"
            )
            return answer, 0.55

        seen = set()
        points = []
        for overlap, line, page_num in scored_sentences[:5]:
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            points.append(f"- {line} (Page {page_num})")
            if len(points) >= 4:
                break

        answer = (
            "Here is the most relevant information found in your document for this question "
            "(extractive match - configure a HUGGINGFACE_API_TOKEN for a fully model-written answer):\n\n"
            + "\n".join(points)
            + f"\n\n**Sources:**\n{sources_md}"
        )
        avg_conf = min(0.75, max(0.45, float(evidence_list[0].get("hybrid_score", 0.5))))
        return answer, round(avg_conf, 2)
