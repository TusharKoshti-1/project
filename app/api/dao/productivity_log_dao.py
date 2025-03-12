from sqlalchemy.orm import Session
from app.api.models import ProductivityLog
from datetime import datetime


class ProductivityLogDAO:
    @staticmethod
    def log_task(db: Session, employee_id: int, task_name: str, start_time: datetime):
        task_entry = ProductivityLog(
            employee_id=employee_id,
            task_name=task_name,
            start_time=start_time,
        )
        db.add(task_entry)
        db.commit()
        db.refresh(task_entry)
        return task_entry

    @staticmethod
    def complete_task(db: Session, task_id: int, end_time: datetime):
        task = db.query(ProductivityLog).filter(ProductivityLog.id == task_id).first()
        if task:
            task.end_time = end_time
            task.is_completed = True
            db.commit()
            db.refresh(task)
        return task

    # 🆕 **New method to log eye closure events**
    @staticmethod
    def log_eye_closure(
        db: Session,
        employee_id: int,
        start_time: datetime,
        end_time: datetime,
        duration: float,
    ):
        eye_closure_entry = ProductivityLog(
            employee_id=employee_id,
            task_name="Eye Closure",
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            is_completed=True,  # Mark as completed since it's a past event
        )
        db.add(eye_closure_entry)
        db.commit()
        db.refresh(eye_closure_entry)
        return eye_closure_entry
