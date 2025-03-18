# app/dao/productivity_dao.py
from sqlalchemy.orm import Session
from app.api.vo.productivity_vo import ProductivityLog
from datetime import datetime


class ProductivityDAO:
    @staticmethod
    def log_event(
        db: Session,
        employee_id: int,
        event_type: str,
        start_time: datetime,
        end_time: datetime = None,
        duration: float = None,
    ):
        """Log a productivity event (e.g., eye closure or recognition)."""
        log_entry = ProductivityLog(
            employee_id=employee_id,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def get_logs_by_employee(db: Session, employee_id: int):
        """Fetch all productivity logs for an employee."""
        return (
            db.query(ProductivityLog)
            .filter(ProductivityLog.employee_id == employee_id)
            .order_by(ProductivityLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_recent_logs(db: Session, limit: int = 100):
        """Fetch the most recent productivity logs."""
        return (
            db.query(ProductivityLog)
            .order_by(ProductivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
