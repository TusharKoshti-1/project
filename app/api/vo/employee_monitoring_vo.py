from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    LargeBinary,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base


class FaceRecognitionLog(Base):
    __tablename__ = "face_recognition_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("Employee.id"), nullable=False)
    recognized_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(String(50), nullable=False)
    frame_id = Column(Integer, ForeignKey("frame_storage.id"), nullable=True)

    employee = relationship("Employee", backref="recognition_logs")
    frame = relationship("FrameStorage", backref="recognition_logs")


class FrameStorage(Base):
    __tablename__ = "frame_storage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("Employee.id"), nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow)
    frame_data = Column(LargeBinary, nullable=False)  # Stores raw image data
    is_processed = Column(Boolean, default=False)

    employee = relationship("Employee", backref="frames")


class ProductivityLog(Base):
    __tablename__ = "productivity_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("Employee.id"), nullable=False)
    task_name = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    employee = relationship("Employee", backref="productivity_logs")


class EyeTrackingData(Base):
    __tablename__ = "eye_tracking_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("Employee.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    focus_level = Column(String(50), nullable=False)
    screen_region = Column(
        String(100), nullable=False
    )  # Stores which part of the screen user looked at

    employee = relationship("Employee", backref="eye_tracking")
