# app/camera.py
import cv2
import logging

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self):
        self.cap = None
        self.initialize()

    def initialize(self):
        try:
            self.cap = cv2.VideoCapture(0)  # 0 is default laptop webcam
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            logger.info("Webcam initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize webcam: {str(e)}")
            self.cap = None

    def get_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                logger.warning("Failed to capture frame")
                return None
        logger.warning("Webcam not available")
        return None

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Webcam released")


camera = None


def init_camera():
    global camera
    camera = Camera()


def get_camera():
    global camera
    if camera is None or camera.cap is None:
        init_camera()
    return camera


def release_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None  # Reset the camera instance
