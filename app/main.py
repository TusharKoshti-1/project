import secrets
import logging
from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from requests import Session
from app.api.controllers import users_controller,employee_controller
from app.service.user_service import check_google_email
from app.utils.auth_utils import create_access_token, verify_access_token
from .config import CLIENT_ID, CLIENT_SECRET, get_db

# Initialize FastAPI application
app = FastAPI()

# Add SessionMiddleware for storing session data
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Initialize OAuth instance
oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        "scope": "email openid profile",
        'redirect_url': 'http://localhost:8000/auth/callback'
    },
)

# Static files (e.g., CSS, JS)
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


# Templates folder for Jinja2
templates = Jinja2Templates(directory="app/frontend/template")

# CORS configuration
origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include users routes
app.include_router(users_controller.router, prefix="/users")
app.include_router(employee_controller.router, prefix="/employee")


@app.get("/")
async def home():
    return RedirectResponse(url='/dashboard')

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """Home route to display the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    """Home route to display the test page."""
    return templates.TemplateResponse("test.html", {"request": request})


# Modify the dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db)  # Add database dependency
):
    # Check if access token exists in cookies
    access_token = request.cookies.get("access_token")
    if not access_token:
        return RedirectResponse(url="/login")
    
    # Verify the access token
    payload = verify_access_token(access_token)
    if not payload:
        return RedirectResponse(url="/login")
    
    # Check if user exists in the database
    try:
        user_email = payload.get("sub")
        check_google_email(db, user_email)  # Verify user existence
    except HTTPException:
        return RedirectResponse(url="/login")
    
    # If all checks pass, show dashboard
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/employee", response_class=HTMLResponse)
async def employee_page(request: Request):
    """Employee page route."""
    return templates.TemplateResponse("employee.html", {"request": request})


@app.get("/add-employee", response_class=HTMLResponse)
async def add_employee_page(request: Request):
    """Add employee page route."""
    return templates.TemplateResponse("add-employee.html", {"request": request})


@app.get("/googlelogin")
async def login(request: Request):
    # Generate a random state to prevent CSRF attacks
    state = secrets.token_urlsafe()
    request.session['oauth_state'] = state  # Store state in session

    # Redirect user to Google's OAuth authorization endpoint
    url = request.url_for('auth')  # The callback URL for OAuth
    return await oauth.google.authorize_redirect(request, url, state=state)

@app.get("/auth")
async def auth(request: Request, db: Session = Depends(get_db)):
    stored_state = request.session.get('oauth_state')
    received_state = request.query_params.get('state')

    if stored_state != received_state:
        logging.error(f"State mismatch: stored {stored_state}, received {received_state}")
        return templates.TemplateResponse(
            'error.html',
            context={'request': request, 'error': "State mismatch, possible CSRF attack."}
        )

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        logging.error(f"OAuthError: {e.error}")
        return templates.TemplateResponse(
            'error.html',
            context={'request': request, 'error': f"OAuthError: {e.error}"}
        )
    
    logging.info(f"Token: {token}")
    user_info = token.get('userinfo')
    logging.info(f"User Info: {user_info}")

    if user_info:
        email = user_info.get('email')

        try:
            # Check if the user exists in the database
            user = check_google_email(db, email)
            logging.info(f"User {email} logged in successfully.")
        except HTTPException as e:
            logging.error(f"User {email} not found in database: {e.detail}")
            return templates.TemplateResponse(
                'error.html',
                context={'request': request, 'error': f"User not found: {e.detail}"}
            )

        # Store user info in session for later use
        request.session['user'] = {
            "email": user.email,
            "role_id": user.role_id
        }

        # Create an access token for the user
        access_token = create_access_token(data={"sub": user.email},expires_delta=60)

        # Clear the state from session after use
        request.session.pop('oauth_state', None)

        # Set the access token in an HTTP-only cookie
        response = RedirectResponse(url='/dashboard')
        response.set_cookie(
            key="access_token", 
            value=access_token, 
            httponly=True,  # HTTP-only flag prevents JS access
            secure=True,    # Make sure to use `secure=True` in production (requires HTTPS)
            max_age=timedelta(minutes=30),  # Token expiration
            samesite="Lax"  # Helps mitigate CSRF attacks
        )

        # Redirect to the dashboard
        return response

    return templates.TemplateResponse(
        'error.html',
        context={'request': request, 'error': "Failed to retrieve user information from Google."}
    )


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password(request: Request):
    """Forgot password page route."""
    return templates.TemplateResponse("forgot-password.html", {"request": request})


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password(request: Request):
    """Reset password page route."""
    return templates.TemplateResponse("resetpassword.html", {"request": request})
