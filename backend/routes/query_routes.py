import os
import json
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.query_model import QueryRecord, QueryEvidence, ChatSession
from models.user_model import User
from routes.auth_routes import get_current_user
from agents.agent_orchestrator import AgentOrchestrator
from utils.file_utils import save_uploaded_file, get_file_extension

router = APIRouter(prefix="/api/query", tags=["Query & Chat Assistant"])

class ChatMessageItem(BaseModel):
    sender: str
    text: str

class ChatQueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default_session"
    domain: str = "All"
    document_id: Optional[int] = None
    top_k: int = 5
    chat_history: Optional[List[ChatMessageItem]] = []

class CreateSessionRequest(BaseModel):
    title: str
    document_id: Optional[int] = None

class RenameSessionRequest(BaseModel):
    title: str

@router.post("")
def ask_chat_question(
    req: ChatQueryRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    history_dicts = [{"sender": m.sender, "text": m.text} for m in req.chat_history] if req.chat_history else []
    
    # Ensure session exists
    session_obj = db.query(ChatSession).filter(ChatSession.session_id == req.session_id).first()
    if not session_obj and req.session_id:
        # Create session record
        title = req.question[:45] + "..." if len(req.question) > 45 else req.question
        session_obj = ChatSession(
            session_id=req.session_id,
            user_id=current_user.id if current_user else None,
            document_id=req.document_id,
            title=title
        )
        db.add(session_obj)
        db.commit()

    result = AgentOrchestrator.execute_multimodal_rag_pipeline(
        db=db,
        question=req.question.strip(),
        domain=req.domain,
        doc_id=req.document_id,
        top_k=req.top_k,
        user_id=current_user.id if current_user else None,
        session_id=req.session_id or "default_session",
        chat_history=history_dicts
    )
    return {"status": "success", "result": result}

@router.post("/with-file")
def ask_chat_question_with_file(
    question: str = Form(...),
    session_id: str = Form("default_session"),
    domain: str = Form("All"),
    document_id: Optional[int] = Form(None),
    top_k: int = Form(5),
    chat_history_json: Optional[str] = Form("[]"),
    attached_file: Optional[UploadFile] = File(None),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
        
    attached_image_path = ""
    attached_info = ""
    
    if attached_file and attached_file.filename:
        ext = get_file_extension(attached_file.filename)
        safe_name = f"query_attach_{uuid.uuid4().hex[:8]}_{attached_file.filename}"
        saved_path = save_uploaded_file(attached_file.file, safe_name)
        attached_image_path = f"/api/static/uploads/{safe_name}"
        
        if ext in ["png", "jpg", "jpeg"]:
            from services.image_service import ImageService
            img_desc = ImageService.generate_image_description(saved_path, question, domain)
            attached_info = f" [Attached User Image: {img_desc['image_type']} - {img_desc['description']}]"
            
    augmented_question = question.strip() + (attached_info if attached_info else "")
    
    history_dicts = []
    try:
        history_dicts = json.loads(chat_history_json)
    except Exception:
        pass

    # Ensure session exists
    session_obj = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session_obj and session_id:
        title = question[:45] + "..." if len(question) > 45 else question
        session_obj = ChatSession(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            document_id=document_id,
            title=title
        )
        db.add(session_obj)
        db.commit()
        
    result = AgentOrchestrator.execute_multimodal_rag_pipeline(
        db=db,
        question=augmented_question,
        domain=domain,
        doc_id=document_id,
        top_k=top_k,
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        chat_history=history_dicts
    )
    
    if attached_image_path:
        result["attached_image_url"] = attached_image_path
        
    return {"status": "success", "result": result}

@router.get("/sessions")
def get_chat_sessions(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(ChatSession)
    if current_user:
        query = query.filter(ChatSession.user_id == current_user.id)
    else:
        query = query.filter(ChatSession.user_id == None)
    
    sessions = query.order_by(ChatSession.updated_at.desc()).all()
    
    # Also find query sessions that might not be in ChatSession yet
    existing_ids = {s.session_id for s in sessions}
    q_records = db.query(QueryRecord.session_id, QueryRecord.question, QueryRecord.created_at).distinct(QueryRecord.session_id)
    if current_user:
        q_records = q_records.filter(QueryRecord.user_id == current_user.id)
    else:
        q_records = q_records.filter(QueryRecord.user_id == None)
    
    additional_sessions = []
    for r in q_records.all():
        s_id = r[0]
        if s_id and s_id not in existing_ids:
            additional_sessions.append({
                "session_id": s_id,
                "title": r[1][:40] if r[1] else "Conversation",
                "created_at": r[2].isoformat() if r[2] else None,
                "time": "Recent"
            })
            
    res_list = [s.to_dict() for s in sessions] + additional_sessions
    return {"status": "success", "sessions": res_list}

@router.post("/sessions")
def create_named_session(
    req: CreateSessionRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Conversation name cannot be empty")
        
    session_id = f"session_{uuid.uuid4().hex[:10]}"
    new_sess = ChatSession(
        session_id=session_id,
        user_id=current_user.id if current_user else None,
        document_id=req.document_id,
        title=req.title.strip()
    )
    db.add(new_sess)
    db.commit()
    db.refresh(new_sess)
    
    return {"status": "success", "session": new_sess.to_dict()}

@router.put("/sessions/{session_id}")
def rename_session(
    session_id: str,
    req: RenameSessionRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Conversation name cannot be empty")
        
    session_obj = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session_obj:
        # Create if not exists
        session_obj = ChatSession(
            session_id=session_id,
            user_id=current_user.id if current_user else None,
            title=req.title.strip()
        )
        db.add(session_obj)
    else:
        if current_user and session_obj.user_id and session_obj.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        session_obj.title = req.title.strip()
        
    db.commit()
    return {"status": "success", "session": session_obj.to_dict()}

@router.get("/sessions/{session_id}")
def get_session_messages(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(QueryRecord).filter(QueryRecord.session_id == session_id)
    if current_user:
        query = query.filter(QueryRecord.user_id == current_user.id)
    else:
        query = query.filter(QueryRecord.user_id == None)
        
    records = query.order_by(QueryRecord.created_at.asc()).all()
    messages = []
    for r in records:
        item = r.to_dict()
        try:
            item["sources"] = json.loads(r.sources_json)
        except Exception:
            item["sources"] = []
        messages.append(item)
        
    session_info = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    return {
        "status": "success",
        "session_id": session_id,
        "title": session_info.title if session_info else "Conversation",
        "messages": messages
    }

@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete QueryRecords
    q_query = db.query(QueryRecord).filter(QueryRecord.session_id == session_id)
    if current_user:
        q_query = q_query.filter(QueryRecord.user_id == current_user.id)
    q_query.delete()
    
    # Delete ChatSession
    s_query = db.query(ChatSession).filter(ChatSession.session_id == session_id)
    if current_user:
        s_query = s_query.filter(ChatSession.user_id == current_user.id)
    s_query.delete()
    
    db.commit()
    return {"status": "success", "message": f"Conversation '{session_id}' and all messages deleted"}
