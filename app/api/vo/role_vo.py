# app/api/vo/role_vo.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.config import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(
        Integer, primary_key=True, autoincrement=False
    )  # Explicitly disable auto-increment
    role_type = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

