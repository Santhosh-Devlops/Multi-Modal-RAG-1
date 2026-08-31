import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True, default="Student Intern")
    role = Column(String(50), default="student")
    is_active = Column(Boolean, default=True)
    is_verified_2fa = Column(Boolean, default=False)
    two_fa_secret = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified_2fa": self.is_verified_2fa,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
