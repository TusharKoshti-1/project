# app/api/dao/user_dao.py
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.api.vo.login_vo import User
from datetime import datetime  # Ensure this is imported


class UserDAO:
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user_data: dict):
        user = User(
            email=user_data["email"],
            role_id=user_data["role_id"],
            password=user_data["password"],
            # Optional fields with defaults
            phone=user_data.get("phone", "0000000000"),
            full_name=user_data.get("full_name", "Unknown"),
            gender=user_data.get("gender", "Not Specified"),
            city=user_data.get("city", "Not Provided"),
            state=user_data.get("state", "Not Provided"),
            created_on=user_data.get("created_on", datetime.utcnow()),
            modified_on=user_data.get("modified_on", datetime.utcnow()),
            is_deleted=user_data.get("is_deleted", False),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def update_user_password(db: Session, user: User, new_password: str):
        user.password = new_password
        user.modified_on = datetime.utcnow()  # Update the modified timestamp
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_users_by_user_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()
