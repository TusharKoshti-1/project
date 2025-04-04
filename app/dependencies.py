# app/dependencies.py
from sqlalchemy.orm import Session
from .config import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
