# app/api/controllers/adminpages_controller.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
from app.api.service.user_service import UserService
from app.api.utils.auth_utils import AuthUtils
from app.dependencies import get_db

router = APIRouter()
auth = AuthUtils()
userservice = UserService()

templates = Jinja2Templates(directory="app/frontend/template")

async def validate_admin(request: Request, db: Session):
    # Common validation logic for all admin routes
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    try:
        user = userservice.check_google_email(db, payload.get("sub"))
        if user.role_id != 0:  # Check if user is actually an admin
            return RedirectResponse(url="/employee/dashboard")
    except HTTPException:
        return RedirectResponse(url="/login")
    
    return user

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("profile.html", {"request": request})

@router.get("/help", response_class=HTMLResponse)
async def help(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("help.html", {"request": request})

@router.get("/employees", response_class=HTMLResponse)
async def employees(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("employee.html", {"request": request})

@router.get("/add-employee", response_class=HTMLResponse)
async def add_employee(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("addEmployee.html", {"request": request})

@router.get("/report", response_class=HTMLResponse)
async def report(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("report.html", {"request": request})

@router.get("/aboutus", response_class=HTMLResponse)
async def aboutus(request: Request, db: Session = Depends(get_db)):
    validation = await validate_admin(request, db)
    if isinstance(validation, RedirectResponse):
        return validation
    return templates.TemplateResponse("aboutUs.html", {"request": request})

@router.get("/logout", response_class=HTMLResponse)
async def admin_logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response