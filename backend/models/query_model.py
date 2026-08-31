import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "document_id": self.document_id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class QueryRecord(Base):
    __tablename__ = "query_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(100), default="default_session", index=True)
    question = Column(Text, nullable=False)
    intent = Column(String(100), default="Direct Lookup")
    domain = Column(String(100), default="Manufacturing")
    requested_modality = Column(String(100), default="Cross-Modal")  # Text, Table, Image, Graph, Numerical, Cross-Modal
    answer = Column(Text, nullable=False)
    external_suggestions = Column(Text, nullable=True)  # Optional internet / general context
    confidence_score = Column(Float, default=0.85)
    groundedness_score = Column(Float, default=0.90)
    sources_json = Column(Text, default="[]")
    verification_status = Column(String(50), default="Verified Grounded")
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    evidence_items = relationship("QueryEvidence", back_populates="query_record", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "question": self.question,
            "intent": self.intent,
            "domain": self.domain,
            "requested_modality": self.requested_modality,
            "answer": self.answer,
            "external_suggestions": self.external_suggestions,
            "confidence_score": self.confidence_score,
            "groundedness_score": self.groundedness_score,
            "sources_json": self.sources_json,
            "verification_status": self.verification_status,
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class QueryEvidence(Base):
    __tablename__ = "query_evidence"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("query_records.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, nullable=True)
    document_id = Column(Integer, nullable=False)
    document_name = Column(String(255), default="")
    page_number = Column(Integer, default=1)
    content_type = Column(String(50), default="text")
    snippet = Column(Text, nullable=False)
    semantic_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    hybrid_score = Column(Float, default=0.0)
    is_selected = Column(Integer, default=1)

    query_record = relationship("QueryRecord", back_populates="evidence_items")

    def to_dict(self):
        return {
            "id": self.id,
            "query_id": self.query_id,
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_name": self.document_name,
            "page_number": self.page_number,
            "content_type": self.content_type,
            "snippet": self.snippet,
            "semantic_score": self.semantic_score,
            "keyword_score": self.keyword_score,
            "hybrid_score": self.hybrid_score,
            "is_selected": bool(self.is_selected)
        }
