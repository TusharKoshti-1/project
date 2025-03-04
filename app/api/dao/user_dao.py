from sqlalchemy.orm import Session
from app.api.vo.login_vo import User

class UserDAO:
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        new_user = User(
            email=user_data['email'],
            password=user_data['password'],
            role_id=user_data['role_id']
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def get_users_by_role(db: Session, role_id: int) -> list[User]:
        return db.query(User).filter(User.role_id == role_id).all()

    @staticmethod
    def update_user_password(db: Session, user: User, new_password: str) -> None:
        user.password = new_password
        db.commit()
        db.refresh(user)