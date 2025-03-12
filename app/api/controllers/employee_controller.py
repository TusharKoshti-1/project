from fastapi import APIRouter, Depends, Form, Request, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas.employee_register import EmployeeRegister
from app.api.service.employee_service import EmployeeService
from app.config import get_db
from pydantic import EmailStr

router = APIRouter()


@router.post("/register")
def register_employee(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    department_name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    face_file: UploadFile = File(),  # Optional file upload
    db: Session = Depends(get_db),
):
    """Registers a new employee with optional profile image upload."""
    try:
        employee_data = EmployeeRegister(
            name=name,
            phone=phone,
            age=age,
            gender=gender,
            department_name=department_name,
            email=email,
            password=password
        )

        # Instantiate the EmployeeService with the database session
        employee_service = EmployeeService(db)

        # Call the register_employee method with employee data and file
        response = employee_service.register_employee(employee_data, face_file)

        return response

    except HTTPException as e:
        raise e  # Reraise HTTP exceptions directly

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred: {str(e)}"
        )
