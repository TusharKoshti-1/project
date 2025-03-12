from sqlalchemy.orm import Session
from dao.productivity_log_dao import ProductivityLogDAO
from datetime import datetime


class ProductivityService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # 📝 Log a new task for an employee
    def log_task(self, employee_id: int, task_name: str, start_time: datetime):
        return ProductivityLogDAO.log_task(
            self.db_session, employee_id, task_name, start_time
        )

    # ✅ Mark a task as completed
    def complete_task(self, task_id: int, end_time: datetime):
        return ProductivityLogDAO.complete_task(self.db_session, task_id, end_time)

    # 👀 Log an eye closure event
    def log_eye_closure(
        self,
        employee_id: int,
        start_time: datetime,
        end_time: datetime,
        duration: float,
    ):
        return ProductivityLogDAO.log_eye_closure(
            self.db_session, employee_id, start_time, end_time, duration
        )

    # 📊 Get productivity stats for an employee
    def get_productivity_stats(self, employee_id: int):
        logs = (
            self.db_session.query(ProductivityLog)
            .filter(ProductivityLog.employee_id == employee_id)
            .all()
        )

        # Calculate total eye closure duration
        total_closed = sum(
            log.duration for log in logs if log.task_name == "Eye Closure"
        )

        # Count completed tasks
        total_tasks_completed = sum(
            1 for log in logs if log.is_completed and log.task_name != "Eye Closure"
        )

        # Count pending tasks
        total_tasks_pending = sum(
            1 for log in logs if not log.is_completed and log.task_name != "Eye Closure"
        )

        return {
            "total_eye_closure_duration": total_closed,
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_pending": total_tasks_pending,
            "logs": logs,
        }
