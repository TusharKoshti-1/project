# app/api/controllers/admin_controller.py
from fastapi import APIRouter, Depends, HTTPException
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

@router.get("/profile/{user_id}")
def get_user_profile(
    user_id: int,
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get profile data for a specific user by their ID
    Parameters:
        user_id: The ID of the user to fetch
    """
    # Fetch the specific user from the database
    user = userservice.get_user_by_id(db, user_id)
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # # Check if current user has permission (e.g., is admin or viewing own profile)
    # if current_user.get('role_id') != 1 and current_user.get('id') != user_id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Not authorized to view this profile"
    #     )
    
    # Prepare user profile response
    response = {
        "id": user.id,
        "name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "created_on": user.created_on,
        # Add more profile fields as needed
        "role_id": user.role_id
    }
    
    return {
        "msg": "User Profile Retrieved Successfully",
        "user": response
    }