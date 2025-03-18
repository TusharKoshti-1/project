# app/api/controllers/productivity_controller.py
from fastapi import APIRouter, UploadFile, File, Depends
from app.api.service.recognition_service import RecognitionService
from app.api.service.productivity_service import ProductivityService
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.api.vo.productivity_vo import ProductivityLog
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/productivity")


def get_recognition_service(db: Session = Depends(get_db)):
    return RecognitionService(db)


def get_productivity_service(
    db: Session = Depends(get_db),
    recognition_service: RecognitionService = Depends(get_recognition_service),
):
    employee_id = recognition_service.get_employee_id()
    return ProductivityService(db, employee_id)


@router.post("/recognize")
async def recognize_employee(
    file: UploadFile = File(...),
    recognition_service: RecognitionService = Depends(get_recognition_service),
):
    try:
        contents = await file.read()
        nparray = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
        if recognition_service.recognize_user(frame):
            return {
                "identity": recognition_service.get_identity(),
                "employee_id": recognition_service.get_employee_id(),
                "status": "recognized",
            }
        return {"identity": "Unknown", "status": "unrecognized"}
    except Exception as e:
        logger.error(f"Error in recognize_employee: {str(e)}")
        return {"error": str(e), "status": "failed"}


@router.post("/track-productivity")
async def track_productivity(
    file: UploadFile = File(...),
    productivity_service: ProductivityService = Depends(get_productivity_service),
):
    try:
        contents = await file.read()
        nparray = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(narray, cv2.IMREAD_COLOR)
        state = productivity_service.process_frame(frame)
        stats = productivity_service.get_productivity_stats()
        return {"current_state": state, "stats": stats, "status": "success"}
    except Exception as e:
        logger.error(f"Error in track_productivity: {str(e)}")
        return {"error": str(e), "status": "failed"}


@router.get("/attendance")
def get_attendance_data(db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    total_days = 30  # Assuming a 30-day work period
    logs = (
        db.query(
            ProductivityLog.employee_id,
            (
                func.count(func.distinct(func.date(ProductivityLog.start_time)))
                * 100.0
                / total_days
            ).label("attendance_rate"),
        )
        .filter(
            ProductivityLog.event_type == "recognized",
            ProductivityLog.start_time >= start_date,
        )
        .group_by(ProductivityLog.employee_id)
        .order_by(
            func.count(func.distinct(func.date(ProductivityLog.start_time))).desc()
        )
        .limit(6)
        .all()
    )
    employee_ids, rates = zip(*logs) if logs else ([], [])
    return {"employee_ids": list(employee_ids), "rates": [round(r, 1) for r in rates]}


@router.get("/performance")
def get_performance_data(db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    work_hours_per_day = 8 * 3600  # 8 hours in seconds
    logs = (
        db.query(
            ProductivityLog.employee_id,
            func.sum(ProductivityLog.duration),
            func.count(func.distinct(func.date(ProductivityLog.start_time))),
        )
        .filter(
            ProductivityLog.event_type == "eye_closed",
            ProductivityLog.start_time >= start_date,
        )
        .group_by(ProductivityLog.employee_id)
        .all()
    )
    result = []
    for emp_id, eye_closed_sum, days in logs:
        total_work_seconds = days * work_hours_per_day - (eye_closed_sum or 0)
        avg_daily_hours = total_work_seconds / 3600 / days
        result.append((emp_id, avg_daily_hours))
    result.sort(key=lambda x: x[1], reverse=True)
    employee_ids, hours = zip(*result[:6]) if result else ([], [])
    return {"employee_ids": list(employee_ids), "hours": [round(h, 2) for h in hours]}


@router.get("/metric-trends")
def get_metric_trends(employee_id: int = 2, db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    logs = (
        db.query(
            func.date(ProductivityLog.start_time).label("date"),
            (func.sum(ProductivityLog.duration) / 60).label("total_minutes"),
        )
        .filter(
            ProductivityLog.employee_id == employee_id,
            ProductivityLog.event_type == "eye_closed",
            ProductivityLog.start_time >= start_date,
        )
        .group_by(func.date(ProductivityLog.start_time))
        .order_by(func.date(ProductivityLog.start_time))
        .all()
    )
    return [{"x": log[0], "y": round(log[1] or 0, 2)} for log in logs]


@router.get("/activity-comparison")
def get_activity_comparison(employee_id: int = 2, db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Recognized duration (assuming each recognition event is a brief presence marker, summing duration if available)
    recog_logs = (
        db.query(
            func.date(ProductivityLog.start_time).label("date"),
            (func.sum(ProductivityLog.duration) / 60).label("recog_minutes"),
        )
        .filter(
            ProductivityLog.employee_id == employee_id,
            ProductivityLog.event_type == "recognized",
            ProductivityLog.start_time >= start_date,
        )
        .group_by(func.date(ProductivityLog.start_time))
        .order_by(func.date(ProductivityLog.start_time))
        .all()
    )
    recog_data = [round(log[1] or 0, 1) for log in recog_logs] + [0] * (
        7 - len(recog_logs)
    )

    # Eye closed duration
    eye_logs = (
        db.query(
            func.date(ProductivityLog.start_time).label("date"),
            (func.sum(ProductivityLog.duration) / 60).label("eye_minutes"),
        )
        .filter(
            ProductivityLog.employee_id == employee_id,
            ProductivityLog.event_type == "eye_closed",
            ProductivityLog.start_time >= start_date,
        )
        .group_by(func.date(ProductivityLog.start_time))
        .order_by(func.date(ProductivityLog.start_time))
        .all()
    )
    eye_data = [round(log[1] or 0, 1) for log in eye_logs] + [0] * (7 - len(eye_logs))

    # Dates for X-axis (last 7 days)
    dates = [
        (end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)
    ]

    return {
        "dates": dates,
        "recognized": recog_data[-7:],  # Last 7 days
        "eye_closed": eye_data[-7:],
    }


@router.get("/performance-distribution")
def get_performance_distribution(employee_id: int = 2, db: Session = Depends(get_db)):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    total_seconds = 7 * 8 * 3600  # 7 days, 8 hours/day
    logs = (
        db.query(ProductivityLog.event_type, func.sum(ProductivityLog.duration))
        .filter(
            ProductivityLog.employee_id == employee_id,
            ProductivityLog.start_time >= start_date,
        )
        .group_by(ProductivityLog.event_type)
        .all()
    )
    events = {"recognized": 0, "eye_closed": 0, "other": 0}
    for event_type, duration in logs:
        events[event_type] = duration or 0
    productive = total_seconds - sum(events.values())
    total = total_seconds or 1  # Avoid division by zero
    return [
        round((events["recognized"] / total) * 100, 1),
        round((events["eye_closed"] / total) * 100, 1),
        round((events["other"] / total) * 100, 1),
        round((productive / total) * 100, 1),
    ]
