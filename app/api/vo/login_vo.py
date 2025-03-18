from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base  # Correct import
from app.api.vo.role_vo import Role


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    role = relationship("Role", backref="users")
    employees = relationship("Employee", back_populates="login")

