from app.dao.user_dao import User, Role
from app.vo.user_vo import UserRegisterVO, UserLoginVO, EmployeeDataVO
from sqlalchemy.orm import Session, joinedload
from app.utils.auth_utils import decode_reset_token, get_password_hash, is_token_expired, verify_password, create_access_token, verify_access_token, generate_reset_token
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

from datetime import datetime, timedelta

def send_password_reset_email(email: str, db: Session):
    print(email)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("email is not in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered."
        )
    reset_token = generate_reset_token(user.id)

    # Add expiration timestamp to the reset link
    expiration = (datetime.utcnow() + timedelta(minutes=10)).timestamp()
    reset_link = f"https://exact-notable-tadpole.ngrok-free.app/reset-password?token={reset_token}&exp={int(expiration)}"

    email_body = f"Click the link to reset your password: {reset_link}"
    print("sending email")
    send_email(email, "Password Reset Instructions", email_body)

def reset_user_password(token: str, new_password: str, db: Session):
    try:
        # Decode and validate the token
        payload = decode_reset_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid token.")

        # Check if the token has expired
        is_token_expired(payload.get("exp"))

        # Find the user by ID
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Hash the new password and update it in the database
        hashed_password = get_password_hash(new_password)
        user.password = hashed_password
        db.commit()

        return {"message": "Password updated successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))