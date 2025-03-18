# app/api/vo/employee_vo.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class Employee(Base):
    __tablename__ = "employees"  # Keep lowercase for consistency

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    department_name = Column(String(100), nullable=False)
    face_image_path = Column(String(255), nullable=True)  # Renamed from face_file
    login_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_deleted = Column(Boolean, default=False)
    last_recognized_on = Column(DateTime, nullable=True)
    created_on = Column(DateTime, default=datetime.utcnow)  # Added from old
    modified_on = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Added from old

    login = relationship("User", back_populates="employees")

