import os
import logging
from uuid import uuid1
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config import supabase, SUPABASE_URL
from app.api.dao.user_dao import UserDAO
from app.api.dao.employee_dao import EmployeeDAO
from app.api.utils.auth_utils import AuthUtils
from datetime import datetime

logger = logging.getLogger(__name__)
recognition_logger = logging.getLogger("recognition")
auth = AuthUtils()


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.bucket_name = os.getenv("SUPABASE_BUCKET_NAME", "images")

    def save_uploaded_image(self, file: UploadFile) -> str:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided.")
        try:
            logger.info(
                f"Uploading to Supabase: {SUPABASE_URL}, Bucket: {self.bucket_name}"
            )
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid1()}{file_extension}"
            file_path = f"employee_images/{unique_filename}"
            file_content = file.file.read()
            logger.info(f"File prepared: {file_path}, Size: {len(file_content)} bytes")
            response = supabase.storage.from_(self.bucket_name).upload(
                file_path, file_content, {"content-type": file.content_type}
            )
            logger.info(f"Supabase upload response: {response}")
            if hasattr(response, "error") and response.error:
                raise HTTPException(
                    status_code=500, detail=f"Image upload failed: {response.error}"
                )
            elif isinstance(response, dict) and "error" in response:
                raise HTTPException(
                    status_code=500, detail=f"Image upload failed: {response['error']}"
                )
            url = f"{SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{file_path}"
            logger.info(f"Image uploaded: {url}")
            return url
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def register_employee(self, employee_data, file: UploadFile = File(...)) -> dict:
        try:
            if UserDAO.get_user_by_email(self.db, employee_data.email):
                raise HTTPException(status_code=400, detail="Email already registered.")
            user = UserDAO.create_user(
                self.db,
                {
                    "email": employee_data.email,
                    "password": auth.get_password_hash(employee_data.password),
                    "role_id": employee_data.role_id,
                },
            )
            profile_image_url = self.save_uploaded_image(file)
            EmployeeDAO.create_employee(
                self.db,
                {
                    "name": employee_data.name,
                    "phone": employee_data.phone,
                    "age": employee_data.age,
                    "gender": employee_data.gender,
                    "department_name": employee_data.department_name,
                    "face_image_path": profile_image_url,
                    "login_id": user.id,
                },
            )
            logger.info(f"Employee {user.id} registered successfully")
            recognition_logger.info(
                f"User recognized and registered: {employee_data.email}, ID: {user.id}, Name: {employee_data.name}"
            )
            return {"message": "Registration successful", "user_id": user.id}
        except HTTPException as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e.detail}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"System error: {str(e)}")
            raise HTTPException(status_code=500, detail="Registration failed.")

    def get_all_employees(self):
        try:
            employees = EmployeeDAO.get_all_employees(self.db)
            users = {user.id: user for user in UserDAO.get_all_users(self.db)}
            result = [
                {
                    "name": emp.name,
                    "jobTitle": "Employee",  # Hardcoded; add to DB if needed
                    "department": emp.department_name,
                    "id": str(emp.id),
                    "email": users.get(emp.login_id).email
                    if users.get(emp.login_id)
                    else "",
                    "phone": emp.phone,
                    "image": emp.face_image_path
                    or "https://via.placeholder.com/80?text=Employee+Photo",
                }
                for emp in employees
            ]
            logger.info(f"Fetched {len(result)} employees from database")
            return result
        except Exception as e:
            logger.error(f"Error in get_all_employees: {str(e)}")
            raise

