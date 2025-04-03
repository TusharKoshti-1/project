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
