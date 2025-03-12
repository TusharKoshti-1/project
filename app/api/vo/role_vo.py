from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from datetime import datetime
from app.config import Base

class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role_type = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

