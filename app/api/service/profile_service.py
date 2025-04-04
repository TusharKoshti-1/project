from fastapi import File, HTTPException, UploadFile
from requests import Session
from app.api.schemas.profile import UpdateProfile
from app.api.dao.profile_dao import ProfileDAO

class ProfileService:
    @staticmethod
    def get_profile(db: Session, user_id: int):
        return ProfileDAO.get_profile(db, user_id)

    @staticmethod
    def update_profile(db: Session, user_id : int, user_update: dict, profile_picture: UploadFile = None):   
        # Logic to update user profile in the database
        profile = ProfileDAO.update_profile(db, user_id, user_update , profile_picture)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
