import secrets
from fastapi import Depends, FastAPI, HTTPException
import logging
from fastapi.responses import RedirectResponse
from requests import Session
from app.api.controllers import users_controller
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from app.service.user_service import check_google_email
from .config import CLIENT_ID, CLIENT_SECRET, get_db

# Initialize FastAPI application
app = FastAPI()

# Add SessionMiddleware for storing session data (important for CSRF protection)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key",)  # Use "None" for cross-site requests)

# Initialize OAuth instance
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth/callback'  # Adjust if you change the redirect URL
    }
)

# Static files (like CSS, JS)
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

# Templates folder for Jinja2
templates = Jinja2Templates(directory="app/frontend/template")

# CORS configuration
origins = ["http://127.0.0.1:5500", "http://127.0.0.1:5501", "http://127.0.0.1:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include users routes
app.include_router(users_controller.router, prefix="/users")

# Home route to show the login page
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Dashboard route (to be displayed after successful login)
@app.get("/dashboard", response_class=HTMLResponse)
async def read_home(request: Request):
    user = request.session.get('user')
    if not user:
        # Redirect to login if the user is not logged in
        return templates.TemplateResponse("login.html", {"request": request})

    return templates.TemplateResponse("dashboard.html", {"request": request})

# Employee page route
@app.get("/employee", response_class=HTMLResponse)
async def read_employee(request: Request):
    return templates.TemplateResponse("employee.html", {"request": request})

# Add employee page route
@app.get("/add-employee", response_class=HTMLResponse)
async def add_employee(request: Request):
    return templates.TemplateResponse("addEmployee.html", {"request": request})

# Login route: this generates a state and redirects to Google OAuth
@app.get("/login")
async def login(request: Request):
    # Generate a random state to prevent CSRF attacks
    state = secrets.token_urlsafe()
    request.session['oauth_state'] = state  # Store state in session

    # Redirect user to Google's OAuth authorization endpoint
    url = request.url_for('auth')  # The callback URL for OAuth
    return await oauth.google.authorize_redirect(request, url, state=state)

# OAuth callback route
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
    print(token)
    user_info = token.get('userinfo')
    print(user_info)

    if user_info:
        email = user_info.get('email')

        try:
            user = check_google_email(db, email)
            logging.info(f"User {email} logged in successfully.")
        except HTTPException as e:
            logging.error(f"User {email} not found in database: {e.detail}")
            return templates.TemplateResponse(
                'error.html',
                context={'request': request, 'error': f"User not found: {e.detail}"}
            )

        request.session['user'] = {
            "email": user.email,
            "role_id": user.role_id
        }

        # Clear the state from session after use
        request.session.pop('oauth_state', None)

        # After successful login, redirect to the dashboard
        return RedirectResponse('/dashboard')

    return templates.TemplateResponse(
        'error.html',
        context={'request': request, 'error': "Failed to retrieve user information from Google."}
    )
