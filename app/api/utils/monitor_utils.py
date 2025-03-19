# app/api/utils/monitor_utils.py
from app.camera import get_camera
import datetime
import time
from sqlalchemy.orm import Session
from app.api.service.recognition_service import RecognitionService
from app.api.service.productivity_service import ProductivityService
from fastapi import HTTPException, BackgroundTasks
import cv2
from app.api.vo.employee_vo import Employee
import logging
from threading import Event  # For stop signal

logger = logging.getLogger(__name__)

# Global dictionary to track active monitoring tasks
active_monitoring_tasks = {}  # {employee_id: Event}


def monitoring_loop(employee_id: int, db: Session):
    camera = get_camera()
    if not camera or not camera.cap:
        logger.error("Webcam not available in monitoring loop")
        return

    productivity_service = ProductivityService(db, employee_id)
    frame_count = 0
    PROCESS_EVERY_NTH_FRAME = 4
    MAX_NO_FACE_SECONDS = 10
    RETRY_DELAY_SECONDS = 5

    # Create a stop event for this employee
    stop_event = Event()
    active_monitoring_tasks[employee_id] = stop_event

    while not stop_event.is_set():  # Run until stopped
        if not camera.cap or not camera.cap.isOpened():
            logger.warning("Webcam disconnected, attempting to reconnect...")
            camera.release()
            time.sleep(RETRY_DELAY_SECONDS)
            camera = get_camera()
            if not camera or not camera.cap:
                logger.error("Failed to reconnect webcam, stopping monitoring")
                break

        frame = camera.get_frame()
        if frame is None:
            logger.warning("Failed to capture frame, retrying...")
            time.sleep(0.1)
            continue

        frame_count += 1
        if frame_count % PROCESS_EVERY_NTH_FRAME == 0:
            scale_factor = 0.5
            small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
            state = productivity_service.process_frame(small_frame)
            logger.debug(f"Employee {employee_id} state: {state}")
            if state is None:
                if "no_face_start" not in locals():
                    no_face_start = datetime.datetime.now()
                elif (
                    datetime.datetime.now() - no_face_start
                ).seconds >= MAX_NO_FACE_SECONDS:
                    logger.info(
                        f"No face detected for {MAX_NO_FACE_SECONDS} seconds, pausing..."
                    )
                    time.sleep(RETRY_DELAY_SECONDS)
                    del no_face_start
            else:
                if "no_face_start" in locals():
                    del no_face_start

    logger.info(f"Monitoring stopped for employee_id: {employee_id}")
    camera.release()
    if employee_id in active_monitoring_tasks:
        del active_monitoring_tasks[employee_id]  # Clean up


def start_recognition_and_monitoring(
    db: Session, background_tasks: BackgroundTasks, login_id: int = None
):
    camera = get_camera()
    if not camera or not camera.cap:
        logger.error("Webcam not available")
        raise HTTPException(status_code=500, detail="Webcam not available")
    recognition_service = RecognitionService(db)
    start_time = datetime.datetime.now()
    timeout = 30
    frame_count = 0
    frame_skip = 2

    while (datetime.datetime.now() - start_time).seconds < timeout:
        frame = camera.get_frame()
        if frame is None:
            logger.error("Failed to capture frame")
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        frame_count += 1
        if frame_count % frame_skip == 0:
            if recognition_service.recognize_user(frame, login_id):  # Pass login_id
                employee_id = recognition_service.get_employee_id()
                if employee_id:
                    logger.info(
                        f"Employee {employee_id} recognized, starting monitoring"
                    )
                    background_tasks.add_task(monitoring_loop, employee_id, db)
                    return employee_id
        time.sleep(0.1)
    logger.warning("No employee recognized within timeout")
    return None
