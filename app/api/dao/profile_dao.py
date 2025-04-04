from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from app.api.vo.login_vo import User
from datetime import datetime
import logging


class ProfileDAO:
    @staticmethod
    def get_profile(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_profile(db: Session, user_id: int, profile_data: dict , profile_picture: UploadFile = None):
        profile = db.query(User).filter(User.id == user_id).first()
        for key, value in profile_data.items():
            if key != "profile_picture":  # Skip profile_picture here, handle separately
                setattr(profile, key, value)

        # Handle profile picture if provided
        if profile_picture:
            content = profile_picture.file.read()  # Read the file content
            profile.profile_picture = content

        db.commit()
        db.refresh(profile)
        return profile
