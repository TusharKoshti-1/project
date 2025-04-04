# app/api/schemas/employee_register.py
from pydantic import BaseModel, EmailStr


class EmployeeRegister(BaseModel):
    name: str
    phone: str
    age: int
    gender: str
    department_name: str
    email: EmailStr
    password: str
    role_id: int = 1  # Default to Employee role

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "name": "Bhupen",
                "phone": "8200472404",
                "age": 21,
                "gender": "Male",
                "department_name": "Developer",
                "email": "bc8080011@gmail.com",
                "password": "room",
                "role_id": 1,
            }
        }
