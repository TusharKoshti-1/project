# app/api/controllers/admin_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.service.user_service import UserService
from app.dependencies import get_db  # Correct import
from app.api.utils.auth_utils import AuthUtils

auth = AuthUtils()
userservice = UserService()

router = APIRouter()

@router.get("/employeedata")
def employeedata(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # We can now access the user info from the current_user
    users = userservice.employee_data(db)  # Get users with role_id 0

    # Prepare a response list of users
    response = []
    for user in users:
        response.append({
            "email": user.email,
            "created_on": user.created_on
        })
    
    return {
        "msg": "Data Get Successfully",
        "users": response  # Return the list of users
    }

@router.get("/admindata")
def admindata(current_user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    # We can now access the user info from the current_user
    users = userservice.admin_data(db)  # Get users with role_id 1

    # Prepare a response list of users
    response = []
    for user in users:
        response.append({
            "email": user.email,
            "created_on": user.created_on
        })
    
    return {
        "msg": "Data Get Successfully",
        "users": response  # Return the list of users
    }
