import sys
from pathlib import Path
import pytest

TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.evaluation_service import EvaluationService

def test_evaluation_metric_calculations():
    retrieved_evidence = [
        {"document_name": "industrial_cnc_machining_manual.pdf", "page_number": 5, "content_text": "Spindle bearing lubrication required every 500 operating hours."},
        {"document_name": "industrial_cnc_machining_manual.pdf", "page_number": 6, "content_text": "Hydraulic oil ISO VG 46 replacement protocol."}
    ]
    generated_answer = "According to industrial_cnc_machining_manual.pdf [Page 5], spindle bearings require lubrication every 500 hours."

    metrics = EvaluationService.evaluate_retrieval_and_answer(
        question="What is the spindle lubrication maintenance interval?",
        expected_doc="industrial_cnc_machining_manual.pdf",
        expected_page=5,
        expected_answer="Spindle bearings require lubrication every 500 hours.",
        retrieved_evidence=retrieved_evidence,
        generated_answer=generated_answer,
        k=5
    )

    assert metrics["is_hit"] is True
    assert metrics["rank"] == 1
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 1.0
    assert metrics["faithfulness"] >= 0.50
    assert metrics["citation_accuracy"] >= 0.80
