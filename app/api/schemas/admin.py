from datetime import datetime
from pydantic import BaseModel, EmailStr 

class EmployeeData(BaseModel):
    email: EmailStr
    created_on: datetime
    role_type: str
    
    class Config:
        from_attributes = True