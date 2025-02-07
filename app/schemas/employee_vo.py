from fastapi import File, Form, UploadFile
from pydantic import BaseModel, EmailStr 
from datetime import datetime

class EmployeeRegister(BaseModel):
    name: str
    age: int
    gender: str
    department_name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

