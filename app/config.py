# app/dependencies.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class OAuthConfig:
    GOOGLE_CLIENT_ID = '754665354965-oosrn97ournnrdbv7njkubnro4li81vv.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


DATABASE_URL = "mysql+pymysql://root:9824@localhost/productivity_monitoring"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
