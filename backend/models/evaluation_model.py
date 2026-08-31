import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(255), default="Multi-Domain Benchmark Dataset")
    total_questions = Column(Integer, default=0)
    recall_at_k = Column(Float, default=0.0)
    precision_at_k = Column(Float, default=0.0)
    mrr = Column(Float, default=0.0)
    hit_rate = Column(Float, default=0.0)
    avg_similarity = Column(Float, default=0.0)
    faithfulness = Column(Float, default=0.0)
    context_relevance = Column(Float, default=0.0)
    answer_relevance = Column(Float, default=0.0)
    citation_accuracy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    items = relationship("EvaluationItem", back_populates="run", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "dataset_name": self.dataset_name,
            "total_questions": self.total_questions,
            "recall_at_k": round(self.recall_at_k, 4),
            "precision_at_k": round(self.precision_at_k, 4),
            "mrr": round(self.mrr, 4),
            "hit_rate": round(self.hit_rate, 4),
            "avg_similarity": round(self.avg_similarity, 4),
            "faithfulness": round(self.faithfulness, 4),
            "context_relevance": round(self.context_relevance, 4),
            "answer_relevance": round(self.answer_relevance, 4),
            "citation_accuracy": round(self.citation_accuracy, 4),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class EvaluationItem(Base):
    __tablename__ = "evaluation_items"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("evaluation_runs.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    domain = Column(String(100), default="Manufacturing")
    content_type = Column(String(50), default="Text")
    expected_doc = Column(String(255), nullable=True)
    expected_page = Column(Integer, nullable=True)
    expected_answer = Column(Text, nullable=True)
    retrieved_doc = Column(String(255), nullable=True)
    retrieved_page = Column(Integer, nullable=True)
    is_hit = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    recall_score = Column(Float, default=0.0)
    faithfulness_score = Column(Float, default=0.0)
    generated_answer = Column(Text, nullable=True)

    run = relationship("EvaluationRun", back_populates="items")

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "question": self.question,
            "domain": self.domain,
            "content_type": self.content_type,
            "expected_doc": self.expected_doc,
            "expected_page": self.expected_page,
            "expected_answer": self.expected_answer,
            "retrieved_doc": self.retrieved_doc,
            "retrieved_page": self.retrieved_page,
            "is_hit": bool(self.is_hit),
            "rank": self.rank,
            "recall_score": round(self.recall_score, 4),
            "faithfulness_score": round(self.faithfulness_score, 4),
            "generated_answer": self.generated_answer
        }
