from sqlalchemy.orm import Session
from app.api.models import EyeTrackingData


class EyeTrackingDataDAO:
    @staticmethod
    def log_eye_tracking(
        db: Session, employee_id: int, focus_level: str, screen_region: str
    ):
        eye_tracking_entry = EyeTrackingData(
            employee_id=employee_id,
            focus_level=focus_level,
            screen_region=screen_region,
        )
        db.add(eye_tracking_entry)
        db.commit()
        db.refresh(eye_tracking_entry)
        return eye_tracking_entry

    @staticmethod
    def get_eye_tracking_by_employee(db: Session, employee_id: int):
        return (
            db.query(EyeTrackingData)
            .filter(EyeTrackingData.employee_id == employee_id)
            .all()
        )
