from app.config import engine, Base
from app.api.vo.employee_vo import Employee
from app.api.vo.login_vo import User
from app.api.vo.role_vo import Role
from app.api.vo.employee_monitoring_vo import (
    FaceRecognitionLog,
    FrameStorage,
    ProductivityLog,
    EyeTrackingData,
)

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
