from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class Employee(Base):
    __tablename__ = "Employee"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10))
    department_name = Column(String(100))
    face_file = Column(String(255), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    login_id = Column(Integer, ForeignKey("login.id"))
    last_recognized_on = Column(DateTime, nullable=True)
