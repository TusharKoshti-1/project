from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    phone: str
    password: str
    full_name: str
    gender: str
    role_id: int = 0  # Default to regular user
    city: str | None = None
    state: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    class Config:
        from_attributes = True
        
class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp: str
    class Config:
        from_attributes = True

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str
    otp: str

    class Config:
        from_attributes = True

