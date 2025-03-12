# face_recognition/detection.py
import cv2
import numpy as np
from scipy.signal import savgol_filter
from collections import deque
import mediapipe as mp
import datetime
import logging

logging.getLogger("mediapipe").setLevel(logging.ERROR)


class ProductivityEyeTracker:
    def __init__(self, productivity_service, employee_id):
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        )
        self.productivity_service = productivity_service
        self.employee_id = employee_id  # Employee ID for logging
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.current_state = "open"
        self.state_start_time = datetime.datetime.now()
        self.closed_duration_threshold = 1.0
        self.min_closed_frames = 5
        self.closed_frame_count = 0
        self.ear_threshold = 0.23
        self.state_history = deque(maxlen=20)

    def process_frame(self, frame):
        results = self.mp_face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        current_time = datetime.datetime.now()

        if not results.multi_face_landmarks:
            if (
                self.current_state == "closed"
                and self.closed_frame_count >= self.min_closed_frames
            ):
                duration = (current_time - self.state_start_time).total_seconds()
                if duration >= self.closed_duration_threshold:
                    self.productivity_service.log_eye_closure(
                        self.employee_id, self.state_start_time, current_time, duration
                    )
                    self.closed_frame_count = 0
            self.current_state = None
            self.state_history.clear()
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        ear = self.calculate_ear(landmarks)
        if ear is None:
            self.current_state = None
            self.closed_frame_count = 0
            self.state_history.clear()
            return None

        self.state_history.append(ear)

        if len(self.state_history) >= 15:
            smoothed_ear = savgol_filter(self.state_history, 15, 2)[-1]
            new_state = "open" if smoothed_ear > self.ear_threshold else "closed"

            if new_state == "closed":
                self.closed_frame_count += 1
                if self.current_state != "closed":
                    self.current_state = "closed"
                    self.state_start_time = current_time
                elif self.closed_frame_count >= self.min_closed_frames:
                    duration = (current_time - self.state_start_time).total_seconds()
                    if duration >= self.closed_duration_threshold:
                        self.productivity_service.log_eye_closure(
                            self.employee_id,
                            self.state_start_time,
                            current_time,
                            duration,
                        )
                        self.state_start_time = current_time
                        self.closed_frame_count = 0
            else:
                if (
                    self.current_state == "closed"
                    and self.closed_frame_count >= self.min_closed_frames
                ):
                    duration = (current_time - self.state_start_time).total_seconds()
                    if duration >= self.closed_duration_threshold:
                        self.productivity_service.log_eye_closure(
                            self.employee_id,
                            self.state_start_time,
                            current_time,
                            duration,
                        )
                        self.closed_frame_count = 0
                self.current_state = "open"
                self.state_start_time = (
                    current_time
                    if self.current_state != "open"
                    else self.state_start_time
                )
        else:
            self.current_state = "open"

        return self.current_state

    def get_productivity_stats(self):
        return self.productivity_service.get_productivity_stats(self.employee_id)
