# app/api/vo/productivity_vo.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.config import Base  # Import Base from config
import datetime


class ProductivityLog(Base):
    __tablename__ = "productivity_logs"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    event_type = Column(String(50), nullable=False)  # Added length
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

