# app/dao/user_dao.py
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config import Base

class User(Base):
    __tablename__ = "login"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)  # Fixed reference to 'role.id'
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    role = relationship("Role", backref="users")  # Use backref to reference users from role


class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    role_type = Column(String(50), nullable=False)
    created_on = Column(DateTime, default=datetime.utcnow)
    modified_on = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

async def get_user_by_email(email: str):
    # Replace this with your database query
    users = [
        {"id": 1, "email": "user1@example.com"},
        {"id": 2, "email": "user2@example.com"}
    ]
    return next((user for user in users if user["email"] == email), None)

