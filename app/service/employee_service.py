import os
from uuid import uuid1, uuid4
from app.dao.user_dao import User
from app.dao.employee_dao import Employee
from sqlalchemy.orm import Session
from app.utils.auth_utils import get_password_hash
from fastapi import File, HTTPException, UploadFile, status
from supabase import create_client


# Supabase Configuration
SUPABASE_URL =  os.environ.get('SUPABASE_URL',None )
SUPABASE_KEY = os.environ.get('SUPABASE_KEY',None )
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to save uploaded image
def save_uploaded_image(file: UploadFile):
    """ Saves the uploaded file and returns its file path. """
    if file:
        bucket_name = "Emp image"  # Ensure this matches your Supabase bucket name
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid1()}{file_extension}"
        file_path = f"employee_images/{unique_filename}"  # Folder inside the bucket

        # Read file content
        file_content = file.file.read()

        # Upload to Supabase Storage
        response = supabase.storage.from_(bucket_name).upload(file_path, file_content, {"content-type": file.content_type})

        if response:
            # Generate public URL for the uploaded file
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"
            return public_url
        
        return None

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

        print(profile_image_url)

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
