from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.api.controllers import (
    admin_controller,
    adminpages_controller,
    auth_controller,
    employee_controller,
    googlelogin_controller,
    page_controller,
)
from app.config import Base, engine

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI()

# Add SessionMiddleware for storing session data
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Create tables before starting the app
logger.info("Creating tables in the database...")
Base.metadata.create_all(bind=engine)
logger.info("Tables created successfully.")

# Static files (e.g., CSS, JS)
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

# CORS configuration
origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include users routes
app.include_router(admin_controller.router, prefix="/admin")
app.include_router(auth_controller.router, prefix="/auth")
app.include_router(employee_controller.router, prefix="/employee")
app.include_router(page_controller.router)
app.include_router(adminpages_controller.router)
app.include_router(googlelogin_controller.router)
