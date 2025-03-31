from fastapi import APIRouter, Depends, HTTPException, status
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


async def validate_employee(request: Request, db: Session):
    # Common validation logic for all employee routes
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")

    payload = auth.verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")

    try:
        user = userservice.check_google_email(db, payload.get("sub"))
        if user.role_id != 1:  # Check if user is actually an employee
            return RedirectResponse(url="/dashboard")
    except HTTPException:
        return RedirectResponse(url="/login")

    return user


@router.get("/employee/dashboard", response_class=HTMLResponse)
async def employee_dashboard(request: Request, db: Session = Depends(get_db)):
    validation = await validate_employee(request, db)
    if isinstance(validation, RedirectResponse):
        return validation

    return templates.TemplateResponse("employee_dashboard.html", {"request": request})


@router.get("/employee/profile", response_class=HTMLResponse)
async def employee_profile(request: Request, db: Session = Depends(get_db)):
    validation = await validate_employee(request, db)
    if isinstance(validation, RedirectResponse):
        return validation

    return templates.TemplateResponse("employee_profile.html", {"request": request})


@router.get("/employee/settings", response_class=HTMLResponse)
async def employee_settings(request: Request, db: Session = Depends(get_db)):
    validation = await validate_employee(request, db)
    if isinstance(validation, RedirectResponse):
        return validation

    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/employee/aboutus", response_class=HTMLResponse)
async def employee_aboutus(request: Request, db: Session = Depends(get_db)):
    validation = await validate_employee(request, db)
    if isinstance(validation, RedirectResponse):
        return validation

    return templates.TemplateResponse("employee_aboutus.html", {"request": request})


@router.get("/employee/logout", response_class=HTMLResponse)
async def employee_logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    response.delete_cookie("employee_id")
    return response

