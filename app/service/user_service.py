from app.dao.user_dao import User, Role, get_user_by_email
from app.vo.user_vo import UserRegisterVO, UserLoginVO, EmployeeDataVO
from sqlalchemy.orm import Session, joinedload
from app.utils.auth_utils import get_password_hash, verify_password, create_access_token, verify_access_token, generate_reset_token
from fastapi import HTTPException, status
from app.utils.email_utils import send_email  # type: ignore

def register_user(db: Session, user_data: UserRegisterVO):
    user = db.query(User).filter(User.email == user_data.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password=hashed_password,
        role_id=user_data.role_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, login_data: UserLoginVO):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # Create an access token upon successful login
    return user

def employee_data(db: Session):
    # Query all Users where role_id is 0
    users = db.query(User).filter(User.role_id == 0).all()
    return users

def admin_data(db: Session):
    # Query all Users where role_id is 1
    users = db.query(User).filter(User.role_id == 1).all()
    return users

def check_google_email(db: Session, email: str):
    # Query the database to check if the email exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist. Please register first."
        )
    return user

async def send_password_reset_email(email: str):
    user = await get_user_by_email(email)
    if not user:
        raise Exception("Email not registered.")

    reset_token = generate_reset_token(user["id"])
    reset_link = f"http://localhost:8000/reset-password?token={reset_token}"
    email_body = f"Click the link to reset your password: {reset_link}"

    await send_email(email, "Password Reset Instructions", email_body)


