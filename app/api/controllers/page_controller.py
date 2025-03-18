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


# Templates folder for Jinja2
templates = Jinja2Templates(directory="app/frontend/template")


@router.get("/")
async def home():
    return RedirectResponse(url="/dashboard")


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Home route to display the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    """Home route to display the test page."""
    return templates.TemplateResponse("test.html", {"request": request})


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request):
    """Forgot password page route."""
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password(request: Request):
    """Reset password page route."""
    return templates.TemplateResponse("reset-password.html", {"request": request})
