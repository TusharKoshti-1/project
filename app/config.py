# app/dependencies.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from supabase import create_client

# Load environment variables from .env file
load_dotenv()

# Environment Variables
CLIENT_ID = os.environ.get('CLIENT_ID')  # Changed to uppercase
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')  # Changed to uppercase
DATABASE_URL = os.environ.get('DATABASE_URL')  # Changed to uppercase


# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Ensure DATABASE_URL is not None
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")


if SUPABASE_URL is None or SUPABASE_KEY is None:
    raise ValueError("Supabase configuration is not set")

# SQLAlchemy engine and session configuration
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)




# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
