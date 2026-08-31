import os
import time
from typing import Dict, Any, List
from pathlib import Path
from sqlalchemy.orm import Session

from models.document_model import (
    Document,
    DocumentPage,
    DocumentChunk,
    DocumentImage,
    DocumentGraph,
    DocumentTable,
    DocumentNumerical
)
from models.agent_model import AgentActivityLog
from services.pdf_service import PDFService
from services.image_service import ImageService
from services.graph_service import GraphService
from services.table_service import TableService
from services.numerical_service import NumericalService
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.vector_store import vector_store
from utils.file_utils import get_file_extension, format_file_size

class DocumentProcessingAgent:
    name = "Document Processing Agent"
    key = "document_agent"
    role_description = "Coordinates multi-format file ingestion and the 5 specialized extractors (Text, Images, Graphs, Tables, Numericals)."
    input_type = "PDF / DOCX / CSV / XLSX / Image"
    output_type = "5-Modality Structured Knowledge & Vector Index"

    @classmethod
    def process_document(cls, db: Session, doc_id: int, trace_id: str) -> Dict[str, Any]:
        start_time = time.time()
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return {"status": "error", "message": "Document not found"}

        doc.status = "Processing"
        db.commit()

        file_path = doc.file_path
        ext = get_file_extension(doc.filename)
        domain = doc.domain

        try:
            pages_data = []
            images_data = []
            graphs_data = []
            tables_data = []
            numericals_data = []
            
            # --- 1. File Type Ingestion & Base Parsing ---
            if ext == "pdf":
                pdf_res = PDFService.extract_pdf_content(file_path, doc.id, domain)
                doc.page_count = pdf_res["page_count"]
                pages_data = pdf_res["pages"]
                raw_images = pdf_res["images"]
                tables_data = pdf_res["tables"]
                
                # Separate Images into Generic Images vs Graphs/Visuals
                for img in raw_images:
                    page_text = pages_data[img["page_number"] - 1]["page_text"] if img["page_number"] <= len(pages_data) else ""
                    
                    # Detect if it's a graph/chart/schematic
                    is_graph_or_chart = any(w in page_text.lower() or w in img.get("image_type", "").lower() for w in [
                        "chart", "graph", "diagram", "schematic", "circuit", "flowchart", "workflow", "histogram", "architecture", "curve"
                    ])
                    
                    if is_graph_or_chart:
                        graph_info = GraphService.analyze_graph_or_visual(img, page_text, domain)
                        graph_info["page_number"] = img["page_number"]
                        graphs_data.append(graph_info)
                    else:
                        images_data.append(img)
                        
                # Extract Numerical Information across all pages
                for p in pages_data:
                    p_nums = NumericalService.extract_numerical_information(p["page_text"], p["page_number"], domain)
                    numericals_data.extend(p_nums)
                
            elif ext in ["csv", "xlsx", "xls"]:
                tab_res = TableService.parse_tabular_file(file_path, ext)
                doc.page_count = 1
                pages_data = [{
                    "page_number": 1,
                    "page_text": f"Tabular Spreadsheet Data ({ext.upper()}) with {tab_res['total_rows']} rows and {tab_res['total_cols']} columns.",
                    "image_count": 0,
                    "table_count": len(tab_res["tables"]),
                    "preview_image_path": ""
                }]
                tables_data = tab_res["tables"]
                # Extract numericals from table cells
                for t in tables_data:
                    p_nums = NumericalService.extract_numerical_information(t.get("natural_language_text", ""), 1, domain)
                    numericals_data.extend(p_nums)
                
            elif ext == "docx":
                import docx
                d = docx.Document(file_path)
                full_text = "\n\n".join([p.text for p in d.paragraphs if p.text.strip()])
                doc.page_count = max(1, len(full_text.split()) // 300)
                pages_data = [{
                    "page_number": 1,
                    "page_text": full_text,
                    "image_count": 0,
                    "table_count": 0,
                    "preview_image_path": ""
                }]
                numericals_data.extend(NumericalService.extract_numerical_information(full_text, 1, domain))
                
            elif ext in ["png", "jpg", "jpeg"]:
                doc.page_count = 1
                desc_info = ImageService.generate_image_description(file_path, "", domain)
                img_obj = {
                    "page_number": 1,
                    "image_path": f"/api/static/uploads/{doc.filename}",
                    "local_filepath": file_path,
                    "image_name": doc.filename,
                    "width": 800,
                    "height": 600,
                    "image_type": desc_info["image_type"],
                    "generated_description": desc_info["description"],
                    "confidence_score": desc_info["confidence"]
                }
                
                # Check if it's a graph/chart
                if any(w in desc_info["description"].lower() for w in ["chart", "graph", "diagram", "schematic", "flowchart"]):
                    g_info = GraphService.analyze_graph_or_visual(img_obj, desc_info["description"], domain)
                    g_info["page_number"] = 1
                    graphs_data.append(g_info)
                else:
                    images_data.append(img_obj)
                    
                pages_data = [{
                    "page_number": 1,
                    "page_text": f"Standalone Visual Asset: {desc_info['description']}",
                    "image_count": 1,
                    "table_count": 0,
                    "preview_image_path": f"/api/static/uploads/{doc.filename}"
                }]

            # --- 2. Save Pages to DB ---
            for p in pages_data:
                p_num = p["page_number"]
                db_page = DocumentPage(
                    document_id=doc.id,
                    page_number=p_num,
                    page_text=p["page_text"],
                    image_count=len([im for im in images_data if im.get("page_number") == p_num]),
                    graph_count=len([gr for gr in graphs_data if gr.get("page_number") == p_num]),
                    table_count=len([tb for tb in tables_data if tb.get("page_number") == p_num]),
                    numerical_count=len([nu for nu in numericals_data if nu.get("page_number") == p_num]),
                    preview_image_path=p.get("preview_image_path", "")
                )
                db.add(db_page)

            # --- 3. Save Images (Image Extractor Agent) ---
            for img in images_data:
                p_num = img.get("page_number", 1)
                img_url = img.get("image_path") or (pages_data[p_num - 1].get("preview_image_path") if p_num <= len(pages_data) else "")
                db_img = DocumentImage(
                    document_id=doc.id,
                    page_number=p_num,
                    image_path=img_url,
                    image_name=img.get("image_name", ""),
                    width=img.get("width", 0),
                    height=img.get("height", 0),
                    image_type=img.get("image_type", "Photo / Figure"),
                    generated_description=img.get("generated_description", "Extracted image figure"),
                    ocr_text=img.get("ocr_text", ""),
                    confidence_score=img.get("confidence_score", 0.90)
                )
                db.add(db_img)

            # --- 4. Save Graphs (Graphs & Visuals Extractor Agent) ---
            for gr in graphs_data:
                p_num = gr.get("page_number", 1)
                gr_url = gr.get("image_path") or (pages_data[p_num - 1].get("preview_image_path") if p_num <= len(pages_data) else "")
                db_gr = DocumentGraph(
                    document_id=doc.id,
                    page_number=p_num,
                    graph_type=gr.get("graph_type", "Process Diagram"),
                    title=gr.get("title", "Diagram"),
                    labels_json=str(gr.get("labels", [])),
                    axis_info=gr.get("axis_info", ""),
                    trend_summary=gr.get("trend_summary", ""),
                    visual_explanation=gr.get("visual_explanation", ""),
                    image_path=gr_url
                )
                db.add(db_gr)

            # --- 5. Save Tables (Table Extractor Agent) ---
            for tbl in tables_data:
                db_tbl = DocumentTable(
                    document_id=doc.id,
                    page_number=tbl.get("page_number", 1),
                    table_index=tbl.get("table_index", 1),
                    title=tbl.get("title", f"Table on Page {tbl.get('page_number', 1)}"),
                    raw_markdown=tbl.get("raw_markdown", ""),
                    structured_json=str(tbl.get("structured_json", [])),
                    natural_language_text=tbl.get("natural_language_text", ""),
                    row_count=tbl.get("row_count", 0),
                    column_count=tbl.get("column_count", 0),
                    image_path=tbl.get("image_path", "")
                )
                db.add(db_tbl)

            # --- 6. Save Numericals (Numerical Extractor Agent) ---
            for num in numericals_data:
                db_num = DocumentNumerical(
                    document_id=doc.id,
                    page_number=num.get("page_number", 1),
                    parameter_name=num.get("parameter_name", "Parameter"),
                    numerical_value=str(num.get("numerical_value", "")),
                    unit=num.get("unit", ""),
                    category=num.get("category", "Measurement"),
                    equation_expression=num.get("equation_expression", ""),
                    equation_number=num.get("equation_number", ""),
                    context_sentence=num.get("context_sentence", "")
                )
                db.add(db_num)

            # Save preview thumbnail on document
            if pages_data and len(pages_data) > 0:
                doc.preview_image_path = pages_data[0].get("preview_image_path", "")

            db.commit()

            # --- 7. Semantic Chunking Across All 5 Modalities & Vector Indexing ---
            text_chunks = ChunkService.chunk_document_text(pages_data, doc.id, domain)
            img_chunks = ChunkService.create_image_chunks(images_data, doc.id, domain)
            
            graph_chunks = []
            for gr in graphs_data:
                graph_chunks.extend(GraphService.graph_to_searchable_chunks(gr, doc.id, domain))

            table_chunks = []
            for tbl in tables_data:
                table_chunks.extend(TableService.table_to_searchable_chunks(tbl, doc.id, domain))

            num_chunks = NumericalService.numerical_to_searchable_chunks(numericals_data, doc.id, domain)

            all_chunks = text_chunks + img_chunks + graph_chunks + table_chunks + num_chunks
            
            vector_batch = []
            meta_batch = []
            
            for c in all_chunks:
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    page_number=c["page_number"],
                    chunk_index=c.get("chunk_index", 0),
                    content_type=c["content_type"],
                    content_text=c["content_text"],
                    token_count=c.get("token_count", 0),
                    domain=domain,
                    metadata_json=c.get("metadata_json", "{}")
                )
                db.add(db_chunk)
                db.flush()
                
                vec = EmbeddingService.get_embedding(c["content_text"])
                vector_batch.append(vec)
                meta_batch.append({
                    "chunk_id": db_chunk.id,
                    "document_id": doc.id,
                    "user_id": doc.user_id,
                    "document_name": doc.filename,
                    "page_number": c["page_number"],
                    "content_type": c["content_type"],
                    "content_text": c["content_text"],
                    "domain": domain
                })
                
            vector_store.add_batch(vector_batch, meta_batch)

            # Update Document Summary Counts
            doc.image_count = len(images_data)
            doc.graph_count = len(graphs_data)
            doc.table_count = len(tables_data)
            doc.numerical_count = len(numericals_data)
            doc.chunk_count = len(all_chunks)
            doc.status = "Completed"
            db.commit()

            elapsed_ms = (time.time() - start_time) * 1000
            
            log = AgentActivityLog(
                trace_id=trace_id,
                agent_name=cls.name,
                action=f"Extracted '{doc.filename}' via 5 Multimodal Agents",
                input_summary=f"File: {doc.filename}, Size: {format_file_size(doc.file_size)}",
                output_summary=(
                    f"✓ {doc.page_count} Pages, {doc.image_count} Images, {doc.graph_count} Graphs, "
                    f"{doc.table_count} Tables, {doc.numerical_count} Numericals, {doc.chunk_count} Chunks."
                ),
                execution_time_ms=elapsed_ms,
                status="Success"
            )
            db.add(log)
            db.commit()

            return {
                "status": "success",
                "page_count": doc.page_count,
                "image_count": doc.image_count,
                "graph_count": doc.graph_count,
                "table_count": doc.table_count,
                "numerical_count": doc.numerical_count,
                "chunk_count": doc.chunk_count
            }

        except Exception as e:
            doc.status = "Failed"
            doc.error_message = str(e)
            db.commit()
            print(f"Error in DocumentProcessingAgent: {e}")
            return {"status": "error", "message": str(e)}
