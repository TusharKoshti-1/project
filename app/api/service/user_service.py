from datetime import datetime, timedelta
import random
import string
from typing import Dict
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.api.vo.login_vo import User
from app.api.schemas.user import UserRegister, UserLogin
from app.api.dao.user_dao import UserDAO
from app.api.utils.auth_utils import AuthUtils
from app.api.utils.email_utils import EmailUtils

auth = AuthUtils()
email_utils = EmailUtils("tusharkoshti01@gmail.com", "xnph emrc zuhb ufdo")
session_store: Dict[str, dict] = {}  # In-memory session store

class UserService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister):
        if UserDAO.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
        hashed_password = auth.get_password_hash(user_data.password)
        return UserDAO.create_user(db, {
        'email': user_data.email,
        'phone': user_data.phone,
        'password': hashed_password,
        'full_name': user_data.full_name,
        'gender': user_data.gender,
        'role_id': user_data.role_id,
        'city': user_data.city,
        'state': user_data.state

        })

    @staticmethod
    def login_user(db: Session, login_data: UserLogin):
        user = UserDAO.get_user_by_email(db, login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        if not auth.verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )
        return user

    @staticmethod
    def get_employee_data(db: Session):
        return UserDAO.get_users_by_role(db, 0)

    @staticmethod
    def get_admin_data(db: Session):
        return UserDAO.get_users_by_role(db, 1)

    @staticmethod
    def check_google_email(db: Session, email: EmailStr):
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first."
            )
        return user

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_password_reset_email(db: Session, email: EmailStr):
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not registered."
            )
        
        otp = UserService.generate_otp()
        session_store[email] = {
            "otp": otp,
            "user_id": user.id,
            "verified": False,
            "expiry": datetime.utcnow() + timedelta(minutes=10)
        }
        
        email_body = f"""
        Your One-Time Password (OTP) for password reset is: {otp}
        This code expires in 10 minutes.
        """
        try:
            email_utils.send_email(email, "Password Reset OTP", email_body)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
        
        return {"message": "OTP sent to your email"}

    @staticmethod
    def verify_otp(db: Session, email: EmailStr, otp: str):
        """Verify the OTP and mark the session as verified"""
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not registered."
            )
        
        session_data = session_store.get(email)
        if not session_data or session_data["expiry"] < datetime.utcnow():
            session_store.pop(email, None)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired or invalid"
            )
        
        stored_otp = session_data["otp"]
        if stored_otp != otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP"
            )
        
        # Mark session as verified
        session_store[email]["verified"] = True
        return {"message": "OTP verified"}

    @staticmethod
    def reset_user_password(email: EmailStr, new_password: str, otp: str, db: Session):
        """Reset the user's password after OTP verification using email"""
        try:
            # First verify the OTP
            UserService.verify_otp(db, email, otp)  # This will raise an exception if verification fails
            
            # Get session data
            session_data = session_store.get(email)
            if not session_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session data not found after verification"
                )
            
            # Find user by email
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Update password
            UserDAO.update_user_password(db, user, auth.get_password_hash(new_password))
            
            # Clean up session
            session_store.pop(email, None)
            
            return {"message": "Password updated successfully"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )