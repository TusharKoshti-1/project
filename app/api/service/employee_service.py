import os
import logging
from uuid import uuid1
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config import supabase, SUPABASE_URL
from app.api.dao.user_dao import UserDAO
from app.api.dao.employee_dao import EmployeeDAO
from app.api.utils.auth_utils import AuthUtils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
auth = AuthUtils()

class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.bucket_name = "Emp image"

    def save_uploaded_image(self, file: UploadFile) -> str:
        """Handles image upload business logic"""
        if not file:
            raise HTTPException(status_code=400, detail="No file provided.")
        
        try:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid1()}{file_extension}"
            file_path = f"employee_images/{unique_filename}"

            # Supabase storage operation
            response = supabase.storage.from_(self.bucket_name).upload(
                file_path, file.file.read(), {"content-type": file.content_type}
            )
            
            if not response:
                raise HTTPException(status_code=500, detail="Image upload failed.")
            
            return f"{SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{file_path}"

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def register_employee(self, employee_data, file: UploadFile = File(...)) -> dict:
        """Orchestrates employee registration process"""
        try:
            # Check existing user
            if UserDAO.get_user_by_email(self.db, employee_data.email):
                raise HTTPException(status_code=400, detail="Email already registered.")
            
            # Create user
            user = UserDAO.create_user(self.db, {
                'email': employee_data.email,
                'password': auth.get_password_hash(employee_data.password),
                'role_id': 0
            })
            
            # Handle image upload
            profile_image_url = self.save_uploaded_image(file) if file else None
            
            # Create employee record
            EmployeeDAO.create_employee(self.db, {
                'name': employee_data.name,
                'age': employee_data.age,
                'gender': employee_data.gender,
                'department_name': employee_data.department_name,
                'face_file': profile_image_url,
                'login_id': user.id
            })
            
            logger.info(f"Employee {user.id} registered successfully")
            return {"message": "Registration successful", "user_id": user.id}

        except HTTPException as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e.detail}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"System error: {str(e)}")
            raise HTTPException(status_code=500, detail="Registration failed.")