
from sqlalchemy.orm import Session
from app.api.models import FrameStorage

class FrameStorageDAO:
    @staticmethod
    def store_frame(db: Session, employee_id: int, frame_data: bytes):
        frame_entry = FrameStorage(
            employee_id=employee_id,
            frame_data=frame_data,
        )
        db.add(frame_entry)
        db.commit()
        db.refresh(frame_entry)
        return frame_entry

    @staticmethod
    def get_frame_by_id(db: Session, frame_id: int):
        return db.query(FrameStorage).filter(FrameStorage.id == frame_id).first()
