from fastapi import HTTPException, status
from requests import Session
from app.api.vo.login_vo import User
from app.api.schemas.user import UserRegister, UserLogin
from app.api.dao.user_dao import UserDAO
from app.api.utils.auth_utils import AuthUtils
from app.api.utils.email_utils import EmailUtils

auth = AuthUtils()
email_utils = EmailUtils("tusharkoshti01@gmail.com", "xnph emrc zuhb ufdo")

class UserService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegister):
        # Check existing user
        if UserDAO.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
        
        # Hash password and create user
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
    def send_password_reset_email(db: Session, email: str):
        user = UserDAO.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not registered."
            )
        
        reset_token = auth.generate_reset_token(user.id)
        reset_link = f"https://exact-notable-tadpole.ngrok-free.app/reset-password?token={reset_token}"
        email_body = f"Click to reset password: {reset_link}"
        email.send_email(email, "Password Reset Instructions", email_body)

    @staticmethod
    def reset_user_password(db: Session, token: str, new_password: str):
        try:
            payload = auth.decode_reset_token(token)
            if auth.is_token_expired(payload.get('exp')):
                raise HTTPException(status_code=400, detail="Expired token.")
            
            user = db.query(User).get(payload['user_id'])
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")
            
            UserDAO.update_user_password(db, user, auth.get_password_hash(new_password))
            return {"message": "Password updated successfully."}

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))