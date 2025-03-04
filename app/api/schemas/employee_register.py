from pydantic import BaseModel, EmailStr 

class EmployeeRegister(BaseModel):
    name: str
    age: int
    gender: str
    department_name: str
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

