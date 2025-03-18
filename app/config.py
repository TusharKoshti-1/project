# app/config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from supabase import create_client, Client

load_dotenv()

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL is None or SUPABASE_SERVICE_ROLE_KEY is None:
    raise ValueError("Supabase environment variables are not set")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

CA_PEM_PATH = os.path.join(os.path.dirname(__file__), "certs", "ca.pem")
engine = create_engine(
    DATABASE_URL,
    connect_args={"ssl": {"ca": CA_PEM_PATH}},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

