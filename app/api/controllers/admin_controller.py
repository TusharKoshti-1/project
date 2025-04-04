# app/api/controllers/admin_controller.py
import base64
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.api.service.profile_service import ProfileService
from app.api.service.user_service import UserService
from app.dependencies import get_db  # Correct import
from app.api.utils.auth_utils import AuthUtils
from app.api.schemas.profile import ProfileResponse, UpdateProfile

auth = AuthUtils()
userservice = UserService()
profileservice = ProfileService()

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
    user = profileservice.get_profile(db, user_id)

    # Convert binary profile picture to base64
    profile_picture_base64 = None
    if user.profile_picture:
        try:
            # Encode binary data to base64
            profile_picture_base64 = base64.b64encode(user.profile_picture).decode('utf-8')
            # Prefix with data URL scheme for image
            profile_picture_base64 = f"data:image/jpeg;base64,{profile_picture_base64}"  # Adjust MIME type if needed (e.g., PNG)
        except Exception as e:
            print(f"Error encoding profile picture: {e}")
            profile_picture_base64 = None
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    response = {
        "id": user.id,
        "name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "profile_picture":profile_picture_base64,  # Adjust as needed
        "created_on": user.created_on,
        # Add more profile fields as needed
        "role_id": user.role_id
    }
    
    return {
        "msg": "User Profile Retrieved Successfully",
        "user": response
    }


@router.put("/profile/{user_id}")
def update_user_profile(
    user_id: int,
    full_name: str = Form(...),  # Use Form for form data
    email: str = Form(...),
    phone: str = Form(...),
    profile_picture: Optional[UploadFile] = File(None),
    current_user: dict = Depends(auth.get_current_user),
    db: Session = Depends(get_db),

):
    try:
        # Convert Pydantic model to dict, exclude profile_picture since it's handled separately
        profile_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone
        }
        
        # Update profile
        updated_profile = profileservice.update_profile(db, user_id, profile_data, profile_picture)

        # Prepare response
        response = {
            "id": updated_profile.id,
            "full_name": updated_profile.full_name,
            "email": updated_profile.email,
            "phone": updated_profile.phone,
            "profile_picture": None if not updated_profile.profile_picture else "Image stored",  # Adjust as needed
            "created_on": updated_profile.created_on,
            "role_id": updated_profile.role_id
        }

        return ProfileResponse(msg="Profile updated successfully", user=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")