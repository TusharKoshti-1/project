from pydantic import BaseModel, EmailStr 


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
