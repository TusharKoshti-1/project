import os
from uuid import uuid1
from fastapi import APIRouter, Depends, Form , Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.employee_vo import EmployeeRegister
from app.service.employee_service import register_employee_service
from app.config import get_db
from pydantic import EmailStr
from fastapi import File,UploadFile


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()


# Function to process and save the uploaded image
def save_uploaded_image(file: UploadFile):
    """ Saves the uploaded file and returns its file path. """
    if file:
        upload_dir = "app/uploads/employee_images"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate a unique file name
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid1()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return file_path
    return None  # Return None if no file uploaded


@router.post("/register")
def register_employee(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    department_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    face_file: UploadFile = File(...),  # Optional file upload
    db: Session = Depends(get_db),
):
    """Registers a new employee with optional profile image upload."""
    employee_data = EmployeeRegister(
        name=name,
        age=age,
        gender=gender,
        department_name=department_name,
        email=email,
        password=password
    )

    response = register_employee_service(db, employee_data, face_file)

    return response