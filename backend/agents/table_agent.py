import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models.agent_model import AgentActivityLog
from services.table_service import TableService

class TableUnderstandingAgent:
    name = "Table Understanding Agent"
    key = "table_agent"
    role_description = "Extracts structured rows and columns from documents, converts tables to Markdown & natural-language assertions, and creates embeddings."
    input_type = "PDF Tabular Areas / CSV / XLSX"
    output_type = "Markdown Matrices & NL Assertions"

    @classmethod
    def process_table_data(cls, db: Session, table_info: Dict[str, Any], doc_id: int, domain: str, trace_id: str) -> List[Dict[str, Any]]:
        start_time = time.time()
        chunks = TableService.table_to_searchable_chunks(table_info, doc_id, domain)
        elapsed_ms = (time.time() - start_time) * 1000

        if trace_id:
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action="Tabular Matrix & Assertion Synthesis",
                input_summary=f"Table Page: {table_info.get('page_number')}, Rows: {table_info.get('row_count')}, Cols: {table_info.get('column_count')}",
                output_summary=f"Generated {len(chunks)} searchable structured table representations.",
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

        return chunks
