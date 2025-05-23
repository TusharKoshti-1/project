# app/api/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.service.user_service import UserService
from app.api.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    OtpVerifyRequest,
    UserRegister,
    UserLogin,
)
from pydantic import BaseModel
from app.dependencies import get_db
from app.api.utils.auth_utils import AuthUtils
from app.api.utils.monitor_utils import (
    start_recognition_and_monitoring,
    active_monitoring_tasks,
)
import logging

auth = AuthUtils()
userservice = UserService()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth")


class LogoutRequest(BaseModel):
    employee_id: int


@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    user = userservice.register_user(db, user_data)
    return {
        "msg": "User registered successfully",
        "user_id": user.id,
        "role_id": user.role_id,
    }


@router.post("/login")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    user = userservice.login_user(db, login_data)
    access_token = auth.create_access_token(data={"sub": user.email})

    # Create base response
    response_content = {
        "msg": "Login successful",
        "access_token": access_token,
        "user_id": user.id,
        "token_type": "bearer",
        "role_id": user.role_id,
        "employee_id": None,
    }

    # Set access token cookie for all authenticated users
    response = JSONResponse(content=response_content)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=3600,
    )

    # Handle employee recognition
    if user.role_id == 1:
        try:
            employee_id = start_recognition_and_monitoring(
                db, background_tasks, login_id=user.id
            )
            if employee_id:
                logger.info(f"Employee {employee_id} recognized and monitoring started")
                # Set employee-specific cookies
                response.set_cookie(
                    key="employee_id",
                    value=str(employee_id),
                    httponly=True,
                    secure=True,
                    samesite="Lax",
                    max_age=3600,
                )
                response_content["employee_id"] = employee_id
            else:
                logger.info("Login succeeded but employee not recognized")

        except HTTPException as e:
            logger.error(f"Employee recognition failed: {e.detail}")
            raise

    else:
        logger.info(f"Admin login: {user.email} (role_id={user.role_id})")

    return response


@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    employee_id = request.employee_id
    if employee_id in active_monitoring_tasks:
        active_monitoring_tasks[employee_id].set()
        del active_monitoring_tasks[employee_id]
        logger.info(f"Monitoring stopped for employee {employee_id} on logout")
        response = JSONResponse(
            content={"msg": "Logout successful, monitoring stopped"}
        )
    else:
        logger.info(f"No active monitoring found for employee {employee_id}")
        response = JSONResponse(content={"msg": "Logout successful"})
    response.delete_cookie("access_token")
    response.delete_cookie("employee_id")
    return response


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        userservice.send_password_reset_email(db, request.email)
        return {"message": "Password reset instructions have been sent to your email."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        userservice.reset_user_password(
            email=request.email, new_password=request.password, otp=request.otp, db=db
        )
        return {"message": "Password reset Successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp")
def verify_otp(request: OtpVerifyRequest, db: Session = Depends(get_db)):
    try:
        userservice.verify_otp(db, request.email, request.otp)
        return {"message": "OTP verified"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

