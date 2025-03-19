from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.requests import Request
from requests import Session
from app.api.service.user_service import UserService
from app.api.utils.auth_utils import AuthUtils
from app.dependencies import get_db


router = APIRouter()
auth = AuthUtils()
userservice = UserService()

templates = Jinja2Templates(directory="app/frontend/template")

@router.get("/employee/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show dashboard
    return templates.TemplateResponse("employee_dashboard.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show profile
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/employee/settings", response_class=HTMLResponse)
async def help(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show help
    return templates.TemplateResponse("settings.html", {"request": request})

@router.get("/employee/aboutus", response_class=HTMLResponse)
async def employess(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show employee
    return templates.TemplateResponse("employee_aboutus.html", {"request": request})

@router.get("/employee/logout", response_class=HTMLResponse)
async def add_employee(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        userservice.check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show add_employee
    return templates.TemplateResponse("login.html", {"request": request})

