
from sqlalchemy.orm import Session
from app.api.models import FaceRecognitionLog

class FaceRecognitionLogDAO:
    @staticmethod
    def log_recognition(db: Session, employee_id: int, confidence_score: str, frame_id: int = None):
        log_entry = FaceRecognitionLog(
            employee_id=employee_id,
            confidence_score=confidence_score,
            frame_id=frame_id,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_logs_by_employee(db: Session, employee_id: int):
        return db.query(FaceRecognitionLog).filter(FaceRecognitionLog.employee_id == employee_id).all()
