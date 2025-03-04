from pydantic import BaseModel, EmailStr 
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role_id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str
