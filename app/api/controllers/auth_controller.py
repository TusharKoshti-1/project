from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.service.user_service import UserService
from app.api.schemas.user import ForgotPasswordRequest, ResetPasswordRequest, UserRegister, UserLogin
from app.config import get_db
from app.api.utils.auth_utils import AuthUtils

auth = AuthUtils()
userservice = UserService()

router = APIRouter()

@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = userservice.register_user(db, user_data)
    print(user_data)
    return {"msg": "User registered successfully", "user_id": user.id, "role_id": user.role_id}


@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = userservice.login_user(db, login_data)  # Validate user credentials

    # Create an access token upon successful login
    access_token = auth.create_access_token(data={"sub": user.email}) 

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

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        userservice.send_password_reset_email(request.email, db)
        return {"message": "Password reset instructions have been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return userservice.reset_user_password(request.token, request.password, db)
