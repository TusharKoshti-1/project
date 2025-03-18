# app/api/service/recognition_service.py
import cv2
import numpy as np
import torch
import datetime
import requests
from io import BytesIO
from facenet_pytorch import InceptionResnetV1, MTCNN
from app.api.dao.employee_dao import EmployeeDAO
from app.api.dao.productivity_dao import ProductivityDAO
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class RecognitionService:
    def __init__(self, db: Session):
        self.db = db
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        self.mtcnn = MTCNN(
            keep_all=True,
            device=self.device,
            margin=40,
            min_face_size=60,
            thresholds=[0.6, 0.7, 0.7],
            post_process=False,
            select_largest=True,
        )
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        self.known_embeddings = []
        self.known_names = []
        self.employee_map = {}
        self.user_identified = False
        self.identified_user = "Unknown"
        self.employee_id = None
        self.dao = EmployeeDAO()
        self.productivity_dao = ProductivityDAO()
        self.load_known_faces()

    def load_known_faces(self):
        logger.info("Loading known faces from database...")
        employees = self.dao.get_all_employees(self.db)
        if not employees:
            logger.warning("No employees found in database")
            return

        seen_names = set()
        for employee in employees:
            name = employee.name.lower()
            if name in seen_names:
                logger.warning(
                    f"Skipping duplicate name: {name} (employee_id: {employee.id})"
                )
                continue
            path = employee.face_image_path
            employee_id = employee.id

            if not path:
                logger.warning(
                    f"No face image path for {name} (employee_id: {employee_id})"
                )
                continue

            try:
                response = requests.get(path)
                response.raise_for_status()
                img = cv2.imdecode(
                    np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR
                )
            except Exception as e:
                logger.error(
                    f"Failed to download or decode image from {path}: {str(e)}"
                )
                continue

            if img is None:
                logger.error(f"Failed to load image: {path}")
                continue
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = self.mtcnn(img_rgb)
            if faces is None or len(faces) == 0:
                logger.warning(f"No faces detected in {path}")
                continue
            embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            logger.debug(
                f"Loaded {name} embedding, shape: {embedding.shape}, employee_id: {employee_id}, path: {path}"
            )
            self.known_embeddings.append(embedding)
            self.known_names.append(name)
            self.employee_map[name] = employee_id  # Store employee_id in map
            seen_names.add(name)

        logger.info(f"Loaded {len(self.known_embeddings)} known faces")
        if not self.known_embeddings:
            logger.warning("No known faces loaded. Recognition will fail.")

    def preprocess_frame(self, frame):
        alpha = 1.5
        beta = 30
        return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

    def recognize_user(self, frame):
        if frame is None or frame.size == 0:
            logger.warning("Invalid frame received")
            return False

        frame = self.preprocess_frame(frame)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = self.mtcnn(img_rgb)
        num_faces = len(faces) if faces is not None else 0
        logger.debug(f"Number of faces detected: {num_faces}")

        if faces is not None and num_faces > 0:
            try:
                for i, face in enumerate(faces):
                    face_np = face.permute(1, 2, 0).cpu().numpy()
                    face_np = (face_np * 255).astype(np.uint8)
                    filename = f"detected_face_{i}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, face_np)
                    logger.debug(f"Saved detected face to {filename}")

                query_embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
                query_embedding = query_embedding / np.linalg.norm(query_embedding)
                similarities = [
                    np.dot(query_embedding, known_embed)
                    for known_embed in self.known_embeddings
                ]

                if similarities:
                    max_index = np.argmax(similarities)
                    score = similarities[max_index]
                    sorted_scores = sorted(similarities, reverse=True)
                    confidence_gap = (
                        sorted_scores[0] - sorted_scores[1]
                        if len(sorted_scores) > 1
                        else 1.0
                    )

                    if score > 0.92 and confidence_gap > 0.03:
                        self.user_identified = True
                        self.identified_user = self.known_names[max_index]
                        self.employee_id = self.employee_map[self.identified_user]
                        logger.info(
                            f"Identified user: {self.identified_user} (employee_id: {self.employee_id}, score: {score}, confidence_gap: {confidence_gap})"
                        )
                        self.dao.update_last_recognition(self.db, self.employee_id)
                        self.productivity_dao.log_event(
                            db=self.db,
                            employee_id=self.employee_id,
                            event_type="recognized",
                            start_time=datetime.datetime.utcnow(),
                        )
                        return True
                    else:
                        logger.debug(
                            f"Score {score} below threshold or confidence gap {confidence_gap} too small"
                        )
                        self.user_identified = False
                        self.identified_user = "Unknown"
                        self.employee_id = None
                        return False
            except Exception as e:
                logger.error(f"Recognition error: {str(e)}")
        else:
            logger.debug("No faces detected in frame")
        return False

    def get_identity(self):
        identity = self.identified_user if self.user_identified else "Unknown"
        logger.debug(f"Returning identity: {identity}")
        return identity

    def get_employee_id(self):
        employee_id = self.employee_id if self.user_identified else None
        logger.debug(f"Returning employee_id: {employee_id}")
        return employee_id
