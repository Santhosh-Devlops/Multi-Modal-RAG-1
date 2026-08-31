from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.agent_model import AgentStatus, AgentActivityLog
from agents.agent_orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("")
def list_agents(db: Session = Depends(get_db)):
    AgentOrchestrator.initialize_agent_registry(db)
    agents = db.query(AgentStatus).order_by(AgentStatus.id).all()
    return {"status": "success", "agents": [a.to_dict() for a in agents]}

@router.get("/activity")
def get_agent_activity(
    trace_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(AgentActivityLog)
    if trace_id:
        query = query.filter(AgentActivityLog.trace_id == trace_id)
    if agent_name and agent_name.lower() != "all":
        query = query.filter(AgentActivityLog.agent_name.ilike(f"%{agent_name}%"))
        
    logs = query.order_by(AgentActivityLog.created_at.desc()).limit(limit).all()
    return {"status": "success", "activity_logs": [l.to_dict() for l in logs]}
