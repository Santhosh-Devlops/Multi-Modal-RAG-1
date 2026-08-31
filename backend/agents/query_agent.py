import time
import re
from typing import Dict, Any
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog

class QueryUnderstandingAgent:
    name = "Query Understanding Agent"
    key = "query_agent"
    role_description = "Determines user intent, domain requirements, numerical lookups, and target modalities (text, table, image, cross-modal)."
    input_type = "Natural Language Question"
    output_type = "Intent, Modality & Routing Specs"

    @classmethod
    def analyze_query(cls, db: Session, question: str, default_domain: str, trace_id: str) -> Dict[str, Any]:
        start_time = time.time()
        q_lower = question.lower()
        
        # 1. Determine Intent
        if any(w in q_lower for w in ["what is the", "maximum", "minimum", "temperature", "pressure", "voltage", "rpm", "tolerance", "limit", "cost", "value"]):
            intent = "Numerical Lookup & Parameter Check"
        elif any(w in q_lower for w in ["diagram", "circuit", "schematic", "figure", "image", "visual", "layout", "drawing", "look like"]):
            intent = "Visual Schematic / Architecture Analysis"
        elif any(w in q_lower for w in ["troubleshoot", "fix", "error", "fault", "warning", "fail", "alarm", "step", "procedure"]):
            intent = "Diagnostic Procedure / Troubleshooting"
        elif any(w in q_lower for w in ["compare", "difference", "versus", "vs", "better", "between"]):
            intent = "Comparative Analysis"
        elif any(w in q_lower for w in ["maintain", "interval", "lubricate", "clean", "service", "schedule"]):
            intent = "Maintenance Protocol Inquiry"
        else:
            intent = "Factual Knowledge & Summary Retrieval"

        # 2. Determine Modality
        is_table = any(w in q_lower for w in ["table", "column", "row", "spec", "parameter", "limit", "matrix", "rate", "cost", "budget", "metric"])
        is_image = any(w in q_lower for w in ["diagram", "image", "circuit", "schematic", "figure", "drawing", "photo", "chart", "graph"])
        
        if is_table and is_image:
            modality = "Cross-Modal (Table + Image)"
        elif is_table:
            modality = "Tabular / Matrix Data"
        elif is_image:
            modality = "Visual Diagram"
        else:
            modality = "Textual Documentation"

        # 3. Detect Domain
        detected_domain = default_domain
        domain_keywords = {
            "Manufacturing": ["cnc", "spindle", "hydraulic", "lubrication", "pump", "coolant", "machining", "torque", "feed rate"],
            "Healthcare": ["mri", "patient", "cryogen", "rf coil", "clinical", "magnetic", "dose", "medical", "scan"],
            "Finance": ["revenue", "capex", "ebitda", "fiscal", "balance sheet", "income", "profit", "expenditure", "audit"],
            "Education": ["robotics", "kinematics", "actuator", "microcontroller", "pwm", "degree of freedom", "algorithm"],
            "Defence": ["avionics", "radar", "aerospace", "telemetry", "flight control", "actuation", "payload", "tactical"]
        }
        for d, kws in domain_keywords.items():
            if any(kw in q_lower for kw in kws):
                detected_domain = d
                break

        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Query Intent & Modality Classification",
                input_summary=f"Question: '{question}'",
                output_summary=f"Intent: {intent} | Modality: {modality} | Domain: {detected_domain}",
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

        return {
            "intent": intent,
            "modality": modality,
            "domain": detected_domain,
            "is_numerical": "numerical" in intent.lower(),
            "target_modality": modality
        }
