from datetime import datetime, timedelta
import random
import string
from fastapi import HTTPException, status
from sqlalchemy.orm import Session  # Corrected import
from app.api.vo.login_vo import User
from app.api.schemas.user import UserRegister, UserLogin
from app.api.dao.user_dao import UserDAO
from app.api.utils.auth_utils import AuthUtils
from app.api.utils.email_utils import EmailUtils

auth = AuthUtils()
email_utils = EmailUtils("tusharkoshti01@gmail.com", "xnph emrc zuhb ufdo")
session_store = {}

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
            'password': hashed_password,
            'role_id': user_data.role_id
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
    def check_google_email(db: Session, email: str):
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found. Please register first."
            )
        return user

    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random OTP of specified length"""
        characters = string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    @staticmethod
    def send_password_reset_email(db: Session, email: str):
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not registered."
            )
        
        otp = UserService.generate_otp()
        session_store[email] = {
            "otp": otp,
            "expiry": datetime.utcnow() + timedelta(minutes=10),
            "user_id": user.id  # Store user_id for later use
        }
        
        email_body = f"""
        Your One-Time Password (OTP) for password reset is: {otp}
        This code expires in 10 minutes.
        """
        email_utils.send_email(email, "Password Reset OTP", email_body)  # Fixed email_utils reference
        return {"message": "OTP sent to your email"}

    @staticmethod
    def verify_otp(db: Session, email: str, otp: str):
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
        
        # Mark session as verified but keep it for password reset
        session_store[email]["verified"] = True
        return {"message": "OTP verified"}

    @staticmethod
    def reset_user_password(db: Session, email: str, new_password: str):
        """Reset the user's password after OTP verification"""
        try:
            session_data = session_store.get(email)
            if not session_data or session_data["expiry"] < datetime.utcnow():
                session_store.pop(email, None)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Session expired or invalid"
                )
            
            if not session_data.get("verified", False):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP not verified"
                )
            
            user = db.query(User).get(session_data["user_id"])
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")
            
            # Update password
            UserDAO.update_user_password(db, user, auth.get_password_hash(new_password))
            
            # Clean up session after successful password reset
            session_store.pop(email, None)
            
            return {"message": "Password updated successfully."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))