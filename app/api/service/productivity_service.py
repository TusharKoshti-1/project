# app/service/productivity_service.py
import cv2
import numpy as np
from scipy.signal import savgol_filter
from collections import deque
import mediapipe as mp
import datetime
from sqlalchemy.orm import Session
from app.api.dao.productivity_dao import ProductivityDAO
import logging

logger = logging.getLogger(__name__)
logging.getLogger("mediapipe").setLevel(logging.ERROR)


class ProductivityService:
    def __init__(self, db: Session, employee_id: int = None):
        self.db = db
        self.employee_id = (
            employee_id  # Optional: Set when tied to a recognized employee
        )
        self.productivity_dao = ProductivityDAO()
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
import cv2
import numpy as np
import torch
import datetime
import requests
from io import BytesIO
from facenet_pytorch import InceptionResnetV1, MTCNN
from app.api.dao.employee_dao import EmployeeDAO
from app.api.dao.productivity_dao import ProductivityDAO
from app.api.vo.employee_vo import Employee  # Add this import
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

    def preprocess_frame(self, frame):
        frame = cv2.resize(frame, (160, 160))
        return cv2.convertScaleAbs(frame, alpha=1.2, beta=20)

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
                img = self.preprocess_frame(img)
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
            if len(faces) > 1:
                logger.warning(f"Multiple faces detected in {path}, using first face")
            embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            logger.debug(
                f"Loaded {name} embedding, shape: {embedding.shape}, employee_id: {employee_id}, path: {path}"
            )
            self.known_embeddings.append(embedding)
            self.known_names.append(name)
            self.employee_map[name] = employee_id
            seen_names.add(name)
        logger.info(f"Loaded {len(self.known_embeddings)} known faces")
        if not self.known_embeddings:
            logger.warning("No known faces loaded. Recognition will fail.")

    def recognize_user(self, frame, login_id=None):
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
                query_embedding = self.resnet(faces[:1]).detach().cpu().numpy()[0]
                query_embedding = query_embedding / np.linalg.norm(query_embedding)
                similarities = [
                    np.dot(query_embedding, known_embed)
                    for known_embed in self.known_embeddings
                ]
                logger.info(
                    f"Similarities: {list(zip(self.known_names, similarities))}"
                )
                if similarities:
                    max_index = np.argmax(similarities)
                    score = similarities[max_index]
                    sorted_scores = sorted(similarities, reverse=True)
                    confidence_gap = (
                        sorted_scores[0] - sorted_scores[1]
                        if len(sorted_scores) > 1
                        else 1.0
                    )
                    if score > 0.80 and confidence_gap > 0.002:  # Relaxed to 0.002
                        self.user_identified = True
                        self.identified_user = self.known_names[max_index]
                        self.employee_id = self.employee_map[self.identified_user]
                        employee = (
                            self.db.query(Employee)
                            .filter(Employee.id == self.employee_id)
                            .first()
                        )
                        if not employee:
                            logger.error(
                                f"Employee with id {self.employee_id} not found"
                            )
                            return False
                        if login_id and employee.login_id != login_id:
                            logger.info(
                                f"Recognized {self.identified_user} (employee_id: {self.employee_id}) but login_id {employee.login_id} != {login_id}"
                            )
                            return False
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
                        logger.info(
                            f"Recognition failed: score={score}, confidence_gap={confidence_gap}"
                        )
                        self.user_identified = False
                        self.identified_user = "Unknown"
                        self.employee_id = None
                        return False
            except Exception as e:
                logger.error(f"Recognition error: {str(e)}")
                return False
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
            refine_landmarks=True,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        )
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.current_state = "open"
        self.state_start_time = datetime.datetime.now()
        self.closed_duration_threshold = 1.0
        self.min_closed_frames = 5
        self.closed_frame_count = 0
        self.total_closed_time = 0.0
        self.log_buffer = []
        self.ear_threshold = 0.23
        self.state_history = deque(maxlen=20)
        logger.info("ProductivityService initialized")

    def calculate_ear(self, landmarks):
        try:

            def eye_aspect_ratio(eye_indices):
                coords = [(landmarks[i].x, landmarks[i].y) for i in eye_indices]
                vertical1 = np.linalg.norm(np.subtract(coords[1], coords[5]))
                vertical2 = np.linalg.norm(np.subtract(coords[2], coords[4]))
                horizontal = np.linalg.norm(np.subtract(coords[0], coords[3]))
                return (vertical1 + vertical2) / (2.0 * horizontal + 1e-6)

            ear = (
                eye_aspect_ratio(self.LEFT_EYE) + eye_aspect_ratio(self.RIGHT_EYE)
            ) / 2
            return ear
        except Exception as e:
            logger.error(f"EAR calculation error: {str(e)}")
            return None

    def process_frame(self, frame):
        if frame is None or frame.size == 0:
            logger.warning("Received invalid frame")
            return None

        results = self.mp_face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        current_time = datetime.datetime.now()

        if not results.multi_face_landmarks:
            if (
                self.current_state == "closed"
                and self.closed_frame_count >= self.min_closed_frames
            ):
                duration = (current_time - self.state_start_time).total_seconds()
                if duration >= self.closed_duration_threshold and self.employee_id:
                    self.log_buffer.append(
                        {
                            "start": self.state_start_time,
                            "end": current_time,
                            "duration": duration,
                        }
                    )
                    self.total_closed_time += duration
                    self.productivity_dao.log_event(
                        db=self.db,
                        employee_id=self.employee_id,
                        event_type="eye_closed",
                        start_time=self.state_start_time,
                        end_time=current_time,
                        duration=duration,
                    )
                    logger.info(f"Eyes closed for {duration:.2f} seconds logged to DB")
                    self.closed_frame_count = 0
            self.current_state = None
            self.state_history.clear()
            logger.debug(f"No face detected at {current_time}")
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        ear = self.calculate_ear(landmarks)
        if ear is None:
            self.current_state = None
            self.closed_frame_count = 0
            self.state_history.clear()
            logger.debug(f"EAR is None at {current_time}")
            return None

        self.state_history.append(ear)
        logger.debug(f"EAR: {ear:.3f}, History length: {len(self.state_history)}")

        if len(self.state_history) >= 15:
            smoothed_ear = savgol_filter(self.state_history, 15, 2)[-1]
            new_state = "open" if smoothed_ear > self.ear_threshold else "closed"
            logger.debug(f"Smoothed EAR: {smoothed_ear:.3f}, New state: {new_state}")

            if new_state == "closed":
                self.closed_frame_count += 1
                if self.current_state != "closed":
                    self.current_state = "closed"
                    self.state_start_time = current_time
                    logger.info("Eyes closed state started")
                elif (
                    self.closed_frame_count >= self.min_closed_frames
                    and self.employee_id
                ):
                    duration = (current_time - self.state_start_time).total_seconds()
                    if duration >= self.closed_duration_threshold:
                        self.log_buffer.append(
                            {
                                "start": self.state_start_time,
                                "end": current_time,
                                "duration": duration,
                            }
                        )
                        self.total_closed_time += duration
                        self.productivity_dao.log_event(
                            db=self.db,
                            employee_id=self.employee_id,
                            event_type="eye_closed",
                            start_time=self.state_start_time,
                            end_time=current_time,
                            duration=duration,
                        )
                        logger.info(
                            f"Eyes closed for {duration:.2f} seconds logged to DB"
                        )
                        self.state_start_time = current_time
                        self.closed_frame_count = 0
            else:
                if (
                    self.current_state == "closed"
                    and self.closed_frame_count >= self.min_closed_frames
                    and self.employee_id
                ):
                    duration = (current_time - self.state_start_time).total_seconds()
                    if duration >= self.closed_duration_threshold:
                        self.log_buffer.append(
                            {
                                "start": self.state_start_time,
                                "end": current_time,
                                "duration": duration,
                            }
                        )
                        self.total_closed_time += duration
                        self.productivity_dao.log_event(
                            db=self.db,
                            employee_id=self.employee_id,
                            event_type="eye_closed",
                            start_time=self.state_start_time,
                            end_time=current_time,
                            duration=duration,
                        )
                        logger.info(
                            f"Eyes closed for {duration:.2f} seconds logged to DB"
                        )
                        self.closed_frame_count = 0
                self.current_state = "open"
                self.state_start_time = (
                    current_time
                    if self.current_state != "open"
                    else self.state_start_time
                )
                logger.debug("Eyes open state detected")
        else:
            self.current_state = "open"
            logger.debug("Initial frames, defaulting to open state")

        return self.current_state

    def get_productivity_stats(self):
        stats = {
            "current_state": self.current_state,
            "total_closed": self.total_closed_time,
            "state_since": self.state_start_time,
            "pending_logs": self.log_buffer.copy(),
        }
        logger.debug(f"Productivity stats retrieved: {stats}")
        return stats

    def clear_log_buffer(self):
        self.log_buffer.clear()
        logger.info("Log buffer cleared")
