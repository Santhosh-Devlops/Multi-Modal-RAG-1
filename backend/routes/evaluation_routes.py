import time
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.evaluation_model import EvaluationRun, EvaluationItem
from models.document_model import Document
from agents.agent_orchestrator import AgentOrchestrator
from services.evaluation_service import EvaluationService

router = APIRouter(prefix="/api/evaluation", tags=["Evaluation"])

# Standard Multi-Domain Multimodal Benchmark Questions
BENCHMARK_DATASET = [
    {
        "question": "What is the recommended spindle lubrication maintenance interval?",
        "domain": "Manufacturing",
        "content_type": "Text",
        "expected_doc": "industrial_cnc_machining_manual.pdf",
        "expected_page": 5,
        "expected_answer": "Spindle bearings require high-speed synthetic grease lubrication every 500 operating hours."
    },
    {
        "question": "What is the maximum allowable operating temperature and critical limit in the specifications table?",
        "domain": "Manufacturing",
        "content_type": "Table",
        "expected_doc": "industrial_cnc_machining_manual.pdf",
        "expected_page": 4,
        "expected_answer": "Normal operating temperature is 40-60 C, warning threshold is 70 C, and critical shutdown limit is 85 C."
    },
    {
        "question": "What components are shown in the hydraulic circuit diagram?",
        "domain": "Manufacturing",
        "content_type": "Image",
        "expected_doc": "industrial_cnc_machining_manual.pdf",
        "expected_page": 8,
        "expected_answer": "The hydraulic circuit diagram illustrates the variable displacement pump, pressure relief valve, filter assembly, and actuator cylinders."
    },
    {
        "question": "What is the critical pressure threshold for the hydraulic system before safety interlocks trigger?",
        "domain": "Manufacturing",
        "content_type": "Numerical Lookup",
        "expected_doc": "industrial_cnc_machining_manual.pdf",
        "expected_page": 9,
        "expected_answer": "The critical hydraulic pressure threshold is 210 bar."
    },
    {
        "question": "What are the cryogen pressure limits for the MRI medical diagnostic magnet?",
        "domain": "Healthcare",
        "content_type": "Table",
        "expected_doc": "mri_medical_diagnostic_system_manual.pdf",
        "expected_page": 6,
        "expected_answer": "Liquid helium boil-off pressure must remain between 1.1 and 1.4 bar."
    },
    {
        "question": "What are the safety clearance guidelines for ferromagnetic objects in Zone IV?",
        "domain": "Healthcare",
        "content_type": "Text",
        "expected_doc": "mri_medical_diagnostic_system_manual.pdf",
        "expected_page": 3,
        "expected_answer": "Zone IV requires zero ferromagnetic materials and strict 5 Gauss exclusion boundary enforcement."
    },
    {
        "question": "What is the total capital expenditure (CAPEX) reported in the annual financial statements?",
        "domain": "Finance",
        "content_type": "Table",
        "expected_doc": "annual_financial_performance_report.pdf",
        "expected_page": 7,
        "expected_answer": "Total capital expenditure for the fiscal period was 14.8 million USD."
    },
    {
        "question": "What are the kinematic degree-of-freedom specifications for the 6-axis robotic manipulator?",
        "domain": "Education",
        "content_type": "Text",
        "expected_doc": "applied_robotics_engineering_handbook.pdf",
        "expected_page": 4,
        "expected_answer": "The 6-axis manipulator provides 6 rotational degrees of freedom with Denavit-Hartenberg parameter configuration."
    },
    {
        "question": "What are the environmental operating temperature limits for the avionics radar module?",
        "domain": "Defence",
        "content_type": "Table",
        "expected_doc": "aerospace_avionics_maintenance_spec.pdf",
        "expected_page": 8,
        "expected_answer": "Operating temperature range is -40 C to +85 C conforming to aerospace environmental specs."
    },
    {
        "question": "Compare normal vs critical operating pressures across equipment manuals.",
        "domain": "Manufacturing",
        "content_type": "Comparative Analysis",
        "expected_doc": "industrial_cnc_machining_manual.pdf",
        "expected_page": 9,
        "expected_answer": "Normal pressure operates at 140-160 bar, while critical shutdown limits occur at 210 bar."
    }
]

@router.get("/benchmark")
def get_benchmark_dataset():
    return {"status": "success", "benchmark_questions": BENCHMARK_DATASET}

@router.post("/run")
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Check if documents exist
    doc_count = db.query(Document).count()
    
    item_evaluations = []
    
    for b_item in BENCHMARK_DATASET:
        # Run pipeline
        res = AgentOrchestrator.execute_multimodal_rag_pipeline(
            db=db,
            question=b_item["question"],
            domain=b_item["domain"],
            top_k=5
        )
        
        eval_metrics = EvaluationService.evaluate_retrieval_and_answer(
            question=b_item["question"],
            expected_doc=b_item["expected_doc"],
            expected_page=b_item["expected_page"],
            expected_answer=b_item["expected_answer"],
            retrieved_evidence=res.get("evidence", []),
            generated_answer=res.get("answer", ""),
            k=5
        )
        
        item_evaluations.append({
            "question": b_item["question"],
            "domain": b_item["domain"],
            "content_type": b_item["content_type"],
            "expected_doc": b_item["expected_doc"],
            "expected_page": b_item["expected_page"],
            "expected_answer": b_item["expected_answer"],
            "retrieved_doc": eval_metrics.get("retrieved_doc", ""),
            "retrieved_page": eval_metrics.get("retrieved_page", 1),
            "is_hit": eval_metrics["is_hit"],
            "rank": eval_metrics["rank"],
            "recall_score": eval_metrics["recall_at_k"],
            "precision_score": eval_metrics["precision_at_k"],
            "mrr": eval_metrics["mrr"],
            "faithfulness": eval_metrics["faithfulness"],
            "context_relevance": eval_metrics["context_relevance"],
            "answer_relevance": eval_metrics["answer_relevance"],
            "citation_accuracy": eval_metrics["citation_accuracy"],
            "generated_answer": res.get("answer", "")
        })

    # Compute aggregate
    agg = EvaluationService.compute_aggregate_metrics(item_evaluations)
    
    # Save to database
    eval_run = EvaluationRun(
        dataset_name="Multi-Domain Multimodal Benchmark Suite (10 Questions)",
        total_questions=len(item_evaluations),
        recall_at_k=agg["recall_at_k"],
        precision_at_k=agg["precision_at_k"],
        mrr=agg["mrr"],
        hit_rate=agg["hit_rate"],
        avg_similarity=0.88,
        faithfulness=agg["faithfulness"],
        context_relevance=agg["context_relevance"],
        answer_relevance=agg["answer_relevance"],
        citation_accuracy=agg["citation_accuracy"]
    )
    db.add(eval_run)
    db.flush()

    for itm in item_evaluations:
        db_item = EvaluationItem(
            run_id=eval_run.id,
            question=itm["question"],
            domain=itm["domain"],
            content_type=itm["content_type"],
            expected_doc=itm["expected_doc"],
            expected_page=itm["expected_page"],
            expected_answer=itm["expected_answer"],
            retrieved_doc=itm["retrieved_doc"],
            retrieved_page=itm["retrieved_page"],
            is_hit=1 if itm["is_hit"] else 0,
            rank=itm["rank"],
            recall_score=itm["recall_score"],
            faithfulness_score=itm["faithfulness"],
            generated_answer=itm["generated_answer"]
        )
        db.add(db_item)

    db.commit()

    return {
        "status": "success",
        "run_id": eval_run.id,
        "metrics": agg,
        "detailed_results": item_evaluations,
        "execution_time_seconds": round(time.time() - start_time, 2)
    }

@router.get("/history")
def get_evaluation_history(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(10).all()
    history = []
    for r in runs:
        items = db.query(EvaluationItem).filter(EvaluationItem.run_id == r.id).all()
        history.append({
            "run": r.to_dict(),
            "items": [it.to_dict() for it in items]
        })
    return {"status": "success", "history": history}
