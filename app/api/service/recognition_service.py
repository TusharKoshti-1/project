import os
import logging
import io
import requests
import numpy as np
import torch
import cv2
import datetime
from uuid import uuid4
from fastapi import File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from facenet_pytorch import InceptionResnetV1, MTCNN
from app.config import supabase, SUPABASE_URL
from app.api.dao.user_dao import UserDAO
from app.api.dao.employee_dao import EmployeeDAO
from app.api.utils.auth_utils import AuthUtils
from app.api.schemas.employee_register import EmployeeRegister

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
auth = AuthUtils()


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.bucket_name = "emp-image"

    def save_uploaded_image(self, file: UploadFile) -> str:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided.")
        try:
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid4()}{file_extension}"
            file_path = f"employee_images/{unique_filename}"
            file_content = file.file.read()
            if not file_content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty.")
            response = supabase.storage.from_(self.bucket_name).upload(
                file_path, io.BytesIO(file_content), {"content-type": file.content_type}
            )
            if response.get("error"):
                raise HTTPException(status_code=500, detail=response["error"])
            return f"{SUPABASE_URL}/storage/v1/object/public/{self.bucket_name}/{file_path}"
        except Exception as e:
            logger.error(f"Image upload error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image upload error: {str(e)}")

    def register_employee(
        self, employee_data: EmployeeRegister, file: UploadFile = None
    ) -> dict:
        try:
            existing_user = UserDAO.get_user_by_email(self.db, employee_data.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered.")
            hashed_password = auth.get_password_hash(employee_data.password)
            user = UserDAO.create_user(
                self.db,
                {
                    "email": employee_data.email,
                    "password": hashed_password,
                    "role_id": 0,
                },
            )
            profile_image_url = self.save_uploaded_image(file) if file else None
            employee = EmployeeDAO.create_employee(
                self.db,
                {
                    "name": employee_data.name,
                    "phone": employee_data.phone,
                    "age": employee_data.age,
                    "gender": employee_data.gender,
                    "department_name": employee_data.department_name,
                    "face_file": profile_image_url,
                    "login_id": user.id,
                },
            )
            logger.info(f"Employee {employee.id} registered successfully")
            return {
                "message": "Registration successful",
                "user_id": user.id,
                "employee_id": employee.id,
            }
        except HTTPException as e:
            self.db.rollback()
            logger.error(f"Registration failed: {e.detail}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected system error: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Registration failed due to an internal error."
            )


class ProductivityRecognizer:
    def __init__(self, db: Session):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.mtcnn = MTCNN(
            keep_all=True,
            device=self.device,
            margin=40,
            min_face_size=60,
            thresholds=[0.6, 0.7, 0.7],
            select_largest=True,
        )
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        self.known_embeddings = []
        self.known_names = []
        self.employee_map = {}
        self.user_identified = False
        self.identified_user = "Unknown"
        self.employee_id = None
        self.dao = EmployeeDAO(db)
        self.load_known_faces()

    def load_known_faces(self):
        employees = self.dao.get_all_employees()
        for employee in employees:
            name, path, employee_id = (
                employee["name"].lower(),
                employee["face_file"],
                employee["employee_id"],
            )
            if not path:
                continue
            img_data = requests.get(path).content
            img = cv2.imdecode(np.frombuffer(img_data, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue
            faces = self.mtcnn(img)
            if faces is None or len(faces) == 0:
                continue
            embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
            embedding /= np.linalg.norm(embedding)
            self.known_embeddings.append(embedding)
            self.known_names.append(name)
            self.employee_map[name] = employee_id

    def recognize_user(self, frame):
        frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=30)
        faces = self.mtcnn(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if faces is None or len(faces) == 0:
            return False
        query_embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
        query_embedding /= np.linalg.norm(query_embedding)
        similarities = [
            np.dot(query_embedding, known_embed)
            for known_embed in self.known_embeddings
        ]
        if similarities:
            max_index = np.argmax(similarities)
            score, confidence_gap = (
                similarities[max_index],
                similarities[max_index] - sorted(similarities, reverse=True)[1]
                if len(similarities) > 1
                else 1.0,
            )
            if score > 0.92 and confidence_gap > 0.03:
                self.user_identified = True
                self.identified_user = self.known_names[max_index]
                self.employee_id = self.employee_map[self.identified_user]
                self.dao.update_last_recognition(self.employee_id)
                return True
        return False

    def get_identity(self):
        return self.identified_user if self.user_identified else "Unknown"

    def get_employee_id(self):
        return self.employee_id if self.user_identified else None
