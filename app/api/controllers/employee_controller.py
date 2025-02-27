from fastapi import APIRouter, Depends, Form , Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.employee_vo import EmployeeRegister
from app.service.employee_service import register_employee_service
from app.config import get_db
from pydantic import EmailStr
from fastapi import File , UploadFile



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
router = APIRouter()

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