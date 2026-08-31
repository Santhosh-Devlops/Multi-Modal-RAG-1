import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from database import Base

class AgentStatus(Base):
    __tablename__ = "agent_status"

    id = Column(Integer, primary_key=True, index=True)
    agent_key = Column(String(50), unique=True, index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    role_description = Column(Text, nullable=False)
    input_type = Column(String(100), nullable=False)
    output_type = Column(String(100), nullable=False)
    status = Column(String(50), default="Online")  # Online, Busy, Idle, Error
    total_tasks_executed = Column(Integer, default=0)
    average_latency_ms = Column(Float, default=0.0)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "agent_key": self.agent_key,
            "agent_name": self.agent_name,
            "role_description": self.role_description,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "status": self.status,
            "total_tasks_executed": self.total_tasks_executed,
            "average_latency_ms": self.average_latency_ms,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None
        }

class AgentActivityLog(Base):
    __tablename__ = "agent_activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), index=True, nullable=False)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(200), nullable=False)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    execution_time_ms = Column(Float, default=0.0)
    status = Column(String(50), default="Success")  # Success, Warning, Error
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "agent_name": self.agent_name,
            "action": self.action,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "execution_time_ms": self.execution_time_ms,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
