import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.document_model import (
    Document,
    DocumentPage,
    DocumentChunk,
    DocumentImage,
    DocumentGraph,
    DocumentTable,
    DocumentNumerical
)
from models.user_model import User
from routes.auth_routes import get_current_user
from agents.document_agent import DocumentProcessingAgent
from services.vector_store import vector_store
from utils.file_utils import is_allowed_file, save_uploaded_file, get_file_extension, format_file_size

router = APIRouter(prefix="/api/documents", tags=["Documents"])

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 Megabytes

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    domain: Optional[str] = Form("General"),
    doc_type: Optional[str] = Form("Document"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Please upload PDF, DOCX, CSV, XLSX, PNG, or JPG."
        )
        
    ext = get_file_extension(file.filename)
    safe_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    saved_path = save_uploaded_file(file.file, safe_filename)
    file_size = os.path.getsize(saved_path)

    # Check 25 MB Limit
    if file_size > MAX_FILE_SIZE_BYTES:
        if os.path.exists(saved_path):
            try:
                os.remove(saved_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=400, 
            detail=f"File size ({format_file_size(file_size)}) exceeds the maximum allowed limit of 25 MB. Please upload a smaller file."
        )

    doc = Document(
        user_id=current_user.id if current_user else None,
        filename=file.filename,
        file_path=saved_path,
        file_type=ext,
        file_size=file_size,
        domain=domain or "General",
        doc_type=doc_type or "Document",
        status="Processing"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    trace_id = f"trace_upload_{doc.id}"
    
    # Process document through the specialized multimodal extractors
    res = DocumentProcessingAgent.process_document(db, doc.id, trace_id)
    db.refresh(doc)
    
    return {
        "status": "success",
        "message": "Document uploaded and indexed successfully across all extractors",
        "document": doc.to_dict(),
        "preview_image_path": doc.preview_image_path or "",
        "formatted_size": format_file_size(file_size),
        "extraction_summary": res
    }

@router.get("")
def list_documents(
    domain: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if current_user:
        # Privacy filter: User's documents + any general docs
        query = query.filter((Document.user_id == current_user.id) | (Document.user_id == None))
    if domain and domain.lower() != "all":
        query = query.filter(Document.domain.ilike(f"%{domain}%"))
    if status and status.lower() != "all":
        query = query.filter(Document.status.ilike(f"%{status}%"))
        
    docs = query.order_by(Document.created_at.desc()).all()
    return {"status": "success", "documents": [d.to_dict() for d in docs]}

@router.get("/{doc_id}")
def get_document_details(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this document")
        
    pages = db.query(DocumentPage).filter(DocumentPage.document_id == doc_id).order_by(DocumentPage.page_number).all()
    return {
        "status": "success",
        "document": doc.to_dict(),
        "pages": [p.to_dict() for p in pages]
    }

@router.get("/{doc_id}/extractors/text")
def get_extracted_text(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    pages = db.query(DocumentPage).filter(DocumentPage.document_id == doc_id).order_by(DocumentPage.page_number).all()
    return {
        "status": "success",
        "extractor": "Text & Layout Extractor Agent",
        "document_name": doc.filename,
        "total_pages": len(pages),
        "pages": [p.to_dict() for p in pages]
    }

@router.get("/{doc_id}/extractors/images")
def get_extracted_images(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    images = db.query(DocumentImage).filter(DocumentImage.document_id == doc_id).order_by(DocumentImage.page_number).all()
    return {
        "status": "success",
        "extractor": "Image Extractor Agent",
        "document_name": doc.filename,
        "total_images": len(images),
        "images": [img.to_dict() for img in images]
    }

@router.get("/{doc_id}/extractors/graphs")
def get_extracted_graphs(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    graphs = db.query(DocumentGraph).filter(DocumentGraph.document_id == doc_id).order_by(DocumentGraph.page_number).all()
    return {
        "status": "success",
        "extractor": "Graphs & Visuals Extractor Agent",
        "document_name": doc.filename,
        "total_graphs": len(graphs),
        "graphs": [gr.to_dict() for gr in graphs]
    }

@router.get("/{doc_id}/extractors/tables")
def get_extracted_tables(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    tables = db.query(DocumentTable).filter(DocumentTable.document_id == doc_id).order_by(DocumentTable.page_number).all()
    return {
        "status": "success",
        "extractor": "Table Extractor Agent",
        "document_name": doc.filename,
        "total_tables": len(tables),
        "tables": [tbl.to_dict() for tbl in tables]
    }

@router.get("/{doc_id}/extractors/numericals")
def get_extracted_numericals(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    numericals = db.query(DocumentNumerical).filter(DocumentNumerical.document_id == doc_id).order_by(DocumentNumerical.page_number).all()
    return {
        "status": "success",
        "extractor": "Numerical & Parameter Extractor Agent",
        "document_name": doc.filename,
        "total_numericals": len(numericals),
        "numericals": [num.to_dict() for num in numericals]
    }

@router.get("/{doc_id}/extractors/equations")
def get_extracted_equations(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    numericals = db.query(DocumentNumerical).filter(DocumentNumerical.document_id == doc_id).order_by(DocumentNumerical.page_number).all()
    # Filter to mathematical equations
    equations = [num.to_dict() for num in numericals if num.category == "Mathematical Equation" or (num.equation_expression and "=" in num.equation_expression)]
    if not equations:
        equations = [num.to_dict() for num in numericals if num.equation_expression]

    return {
        "status": "success",
        "extractor": "Mathematical & Equation Extractor Agent",
        "document_name": doc.filename,
        "total_equations": len(equations),
        "equations": equations
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user and doc.user_id and doc.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    vector_store.delete_document(doc_id)
    
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass
        
    db.delete(doc)
    db.commit()
    return {"status": "success", "message": f"Document '{doc.filename}' and all extracted items deleted"}
