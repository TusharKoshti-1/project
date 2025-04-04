from pydantic import BaseModel, EmailStr
from fastapi import Form, UploadFile, File

class UpdateProfile(BaseModel):
    full_name: str = Form(...)
    email: EmailStr = Form(...)
    phone: str = Form(...)
    profile_picture: UploadFile = File(None)  # Changed to None for optional file

    class Config:
        from_attributes = True

class ProfileResponse(BaseModel):
    msg: str
    user: dict

    class Config:
        from_attributes = True