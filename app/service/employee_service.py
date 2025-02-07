import os
from uuid import uuid4
from app.dao.user_dao import User
from app.dao.employee_dao import Employee
from sqlalchemy.orm import Session
from app.utils.auth_utils import get_password_hash
from fastapi import File, HTTPException, UploadFile, status

UPLOAD_DIR = "app/uploads/employee_images"
PUBLIC_UPLOAD_DIR = "/upload/employee_images"  # Relative path for serving files

# Function to save uploaded image
def save_uploaded_image(file: UploadFile):
    """ Saves the uploaded file and returns its relative path. """
    if not file:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure directory exists

    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Return relative URL path instead of absolute path
    return f"{PUBLIC_UPLOAD_DIR}/{unique_filename}"

# Employee registration function
def register_employee_service(db: Session, employee_data, file: UploadFile = File(...)):
    """ Registers a new employee and handles image upload. """
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == employee_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )

        # Hash password
        hashed_password = get_password_hash(employee_data.password)

        # Save profile image
        profile_image_url = save_uploaded_image(file) if file else None

        # Create new user
        new_user = User(
            email=employee_data.email,
            password=hashed_password,
            role_id=0,  # Employees have role_id = 0
        )
        db.add(new_user)
        db.flush()  # Get new_user.id before commit

        # Create new employee record
        new_employee = Employee(
            name=employee_data.name,
            age=employee_data.age,
            gender=employee_data.gender,
            department_name=employee_data.department_name,
            face_file=profile_image_url,  # Store image URL
            login_id=new_user.id
        )
        db.add(new_employee)
        db.commit()  # Commit both user and employee
        db.refresh(new_user)

        return {
            "msg": "User registered successfully",
            "user_id": new_user.id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
