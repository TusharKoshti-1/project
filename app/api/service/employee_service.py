import os
import logging
from uuid import uuid4
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config import supabase, SUPABASE_URL
from app.api.dao.user_dao import UserDAO
from app.api.dao.employee_dao import EmployeeDAO
from app.api.utils.auth_utils import AuthUtils
from app.api.schemas.employee_register import EmployeeRegister

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
auth = AuthUtils()


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.bucket_name = "Emp image"

    def save_uploaded_image(self, file: UploadFile) -> str:
        """Handles image upload business logic to Supabase"""
        if not file:
            raise HTTPException(status_code=400, detail="No file provided.")

        try:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            file_path = f"employee_images/{unique_filename}"

            # Read file content before passing to Supabase
            file_content = file.file.read()
            if not file_content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")

            # Upload to Supabase storage
            response = supabase.storage.from_(self.bucket_name).upload(
                file_path, file_content, {"content-type": file.content_type}
            )

            if response.get("error"):
                raise HTTPException(status_code=500, detail="Image upload failed.")

            return f"{SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{file_path}"

        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

    def register_employee(
        self, employee_data: EmployeeRegister, file: UploadFile = None
    ) -> dict:
        """Registers an employee and uploads profile image"""
        try:
            # Check if email is already registered
            existing_user = UserDAO.get_user_by_email(self.db, employee_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered.")

            # Hash password before storing
            hashed_password = auth.get_password_hash(employee_data.password)

            # Create user entry
            user = UserDAO.create_user(
                self.db,
                {
                    "email": employee_data.email,
                    "password": hashed_password,
                    "role_id": 0,  # Default role for employees
                },
            )

            # Upload profile image if provided
            profile_image_url = self.save_uploaded_image(file) if file else None

            # Create employee record linked to user login ID
            employee = EmployeeDAO.create_employee(
                self.db,
                {
                    "name": employee_data.name,
                    "phone": employee_data.phone,
                    "age": employee_data.age,
                    "gender": employee_data.gender,
                    "department_name": employee_data.department_name,
                    "face_file": profile_image_url,
                    "login_id": user.id,
                },
            )

            logger.info(f"Employee {employee.id} registered successfully")
            return {
                "message": "Registration successful",
                "user_id": user.id,
                "employee_id": employee.id,
            }

        except HTTPException as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e.detail}")
            raise

        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected system error: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Registration failed due to an internal error."
            )
