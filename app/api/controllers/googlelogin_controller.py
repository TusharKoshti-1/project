# app/api/controllers/googlelogin_controller.py
import secrets
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from authlib.integrations.starlette_client import OAuth, OAuthError
from sqlalchemy.orm import Session
from app.api.service.user_service import UserService
from app.api.utils.auth_utils import AuthUtils
from app.api.utils.monitor_utils import start_recognition_and_monitoring
from app.config import CLIENT_ID, CLIENT_SECRET
from app.dependencies import get_db

router = APIRouter(prefix="/google")
auth = AuthUtils()
userservice = UserService()
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/frontend/template")

oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "scope": "email openid profile",
        "redirect_url": "http://localhost:8000/auth/callback",
    },
)


@router.get("/login")
async def login(request: Request):
    state = secrets.token_urlsafe()
    request.session["oauth_state"] = state
    url = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, url, state=state)


@router.get("/auth")
async def auth(
    request: Request,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,  # Fixed from BackgroundTasks()
):
    stored_state = request.session.get("oauth_state")
    received_state = request.query_params.get("state")

    if stored_state != received_state:
        logger.error(
            f"State mismatch: stored {stored_state}, received {received_state}"
        )
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error": "State mismatch, possible CSRF attack.",
            },
        )

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        logger.error(f"OAuthError: {e.error}")
        return templates.TemplateResponse(
            "error.html",
            context={"request": request, "error": f"OAuthError: {e.error}"},
        )

    user_info = token.get("userinfo")
    if not user_info:
        return templates.TemplateResponse(
            "error.html",
            context={
                "request": request,
                "error": "Failed to retrieve user information.",
            },
        )

    email = user_info.get("email")
    user = userservice.check_google_email(db, email)
    if not user:
        logger.error(f"User {email} not found in database")
        return templates.TemplateResponse(
            "error.html",
            context={"request": request, "error": "User not found."},
        )

    # Start recognition and monitoring only if user is an employee (role_id = 1)
    employee_id = None
    if user.role_id == 1:  # Assuming role_id = 1 is for employees
        try:
            employee_id = start_recognition_and_monitoring(
                db, background_tasks, login_id=user.id
            )
            if not employee_id:
                logger.info("Login succeeded but employee not recognized")
            else:
                logger.info(f"Employee {employee_id} recognized and monitoring started")
                request.session["employee_id"] = employee_id
        except HTTPException as e:
            logger.warning(f"Monitoring failed: {e.detail}")
            employee_id = None
    else:
        logger.info(
            f"User {email} is an admin (role_id = {user.role_id}), skipping monitoring"
        )

    request.session["user"] = {"email": user.email, "role_id": user.role_id}
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=60)
    )
    request.session.pop("oauth_state", None)

    response = RedirectResponse(url="/dashboard")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        max_age=timedelta(minutes=30).total_seconds(),
        samesite="Lax",
    )
    return response

