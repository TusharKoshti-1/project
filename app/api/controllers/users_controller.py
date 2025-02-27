from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.service.user_service import register_user, login_user, employee_data, admin_data, reset_user_password, send_password_reset_email 
from app.schemas.user_vo import ForgotPasswordRequest, ResetPasswordRequest, UserRegisterVO, UserLoginVO, EmployeeDataVO
from app.config import get_db
from app.utils.auth_utils import verify_access_token , create_access_token
from pydantic import BaseModel
from datetime import timedelta

# OAuth2PasswordBearer is used for retrieving the token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify and decode the token
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload  # This will contain the user info, e.g., email

router = APIRouter()

@router.post("/register")
def register(user_data: UserRegisterVO, db: Session = Depends(get_db)):
    user = register_user(db, user_data)
    print(user_data)
    return {"msg": "User registered successfully", "user_id": user.id, "role_id": user.role_id}


@router.post("/login")
def login(login_data: UserLoginVO, db: Session = Depends(get_db)):
    user = login_user(db, login_data)  # Validate user credentials

    # Create an access token upon successful login
    access_token = create_access_token(data={"sub": user.email}) 

    response = JSONResponse(content={
        "msg": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role_id": user.role_id
    })
    
    # Set access token in cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevent JavaScript access (XSS protection)
        secure=True,  # Use Secure cookies if running over HTTPS
        samesite="Lax",  # Adjust as needed
        max_age=3600  # Token expiry in seconds
    )
    
    return response
@router.get("/employeedata")
def employeedata(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # We can now access the user info from the current_user
    users = employee_data(db)  # Get users with role_id 0

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
def admindata(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    # We can now access the user info from the current_user
    users = admin_data(db)  # Get users with role_id 1

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
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        send_password_reset_email(request.email, db)
        return {"message": "Password reset instructions have been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return reset_user_password(request.token, request.password, db)
