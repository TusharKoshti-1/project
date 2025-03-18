from fastapi import APIRouter, Depends, Form, Request, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas.employee_register import EmployeeRegister
from app.api.service.employee_service import EmployeeService
from app.dependencies import get_db
from pydantic import EmailStr
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
    face_file: UploadFile = File(...),
    role_id: int = Form(default=1),
    db: Session = Depends(get_db),
):
    logger.info(f"Request received at /employees/register for {email}")
    try:
        employee_data = EmployeeRegister(
            name=name,
            phone=phone,
            age=age,
            gender=gender,
            department_name=department_name,
            email=email,
            password=password,
            role_id=role_id,
        )
        employee_service = EmployeeService(db)
        response = employee_service.register_employee(employee_data, face_file)
        logger.info(f"Registration successful for {email}")
        return response
    except HTTPException as e:
        logger.error(f"HTTP error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@router.get("/")
def get_all_employees(db: Session = Depends(get_db)):
    logger.info("Fetching all employees from database")
    try:
        employee_service = EmployeeService(db)
        employees = employee_service.get_all_employees()
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch employees")
