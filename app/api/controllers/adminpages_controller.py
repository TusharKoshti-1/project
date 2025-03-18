# app/api/controllers/adminpages_controller.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.requests import Request
from sqlalchemy.orm import Session  # Added for clarity
from app.api.service.user_service import UserService
from app.api.utils.auth_utils import AuthUtils
from app.dependencies import get_db  # Corrected import

router = APIRouter()
auth = AuthUtils()
userservice = UserService()

templates = Jinja2Templates(directory="app/frontend/template")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/help", response_class=HTMLResponse)
async def help(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("help.html", {"request": request})


@router.get("/employees", response_class=HTMLResponse)
async def employess(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("employee.html", {"request": request})


@router.get("/add-employee", response_class=HTMLResponse)
async def add_employee(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("addEmployee.html", {"request": request})


@router.get("/report", response_class=HTMLResponse)
async def report(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("report.html", {"request": request})


@router.get("/aboutus", response_class=HTMLResponse)
async def aboutus(request: Request, db: Session = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)
    except HTTPException:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("aboutUs.html", {"request": request})

