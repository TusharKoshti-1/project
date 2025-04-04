# capture_image.py
import cv2

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imwrite("bhupen1_live.jpg", frame)
cap.release()
