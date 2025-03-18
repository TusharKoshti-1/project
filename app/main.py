# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from app.api.controllers import (
    admin_controller,
    adminpages_controller,
    auth_controller,
    employee_controller,
    googlelogin_controller,
    page_controller,
    productivity_controller,
)
from app.config import (
    CLIENT_ID,
    CLIENT_SECRET,
    Base,
    engine,
    SessionLocal,
)  # Correct import
from app.logging_config import setup_logging
from app.api.vo.role_vo import Role
from app.camera import init_camera, release_camera
import logging

app = FastAPI()
setup_logging()
logger = logging.getLogger(__name__)

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
app.include_router(productivity_controller.router)
app.include_router(admin_controller.router, prefix="/admin")
app.include_router(auth_controller.router)
app.include_router(employee_controller.router, prefix="/employees")
app.include_router(page_controller.router)
app.include_router(employeepage_controller.router)
app.include_router(adminpages_controller.router)
app.include_router(googlelogin_controller.router)
app.include_router(
    productivity_controller.router, prefix="/api/productivity", tags=["productivity"]
)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Connecting to database: {engine.url}")
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            for role_id, role_type in [(0, "Admin"), (1, "Employee")]:
                if (
                    not db.query(Role)
                    .filter(Role.id == role_id, Role.is_deleted == 0)
                    .first()
                ):
                    db.add(Role(id=role_id, role_type=role_type, is_deleted=False))
                    logger.info(f"Seeded role: {role_type}")
            db.commit()
            logger.info("Database initialization and seeding completed")
        init_camera()
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    release_camera()
