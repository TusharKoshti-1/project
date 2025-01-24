# app/vo/user_vo.py
from pydantic import BaseModel, EmailStr 
from datetime import datetime
class UserRegisterVO(BaseModel):
    email: EmailStr
    password: str
    role_id: int

    class Config:
        orm_mode = True

class UserLoginVO(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True

class EmployeeDataVO(BaseModel):
    email: EmailStr
    created_on: datetime
    role_type: str
    
    class Config:
        orm_mode = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
