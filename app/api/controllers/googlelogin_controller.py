import secrets
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from requests import Session
from app.api.service.user_service import UserService
from app.api.utils.auth_utils import AuthUtils
from app.config import CLIENT_ID, CLIENT_SECRET, get_db

router = APIRouter()
auth = AuthUtils()
userservice = UserService()

# Templates folder for Jinja2
templates = Jinja2Templates(directory="app/frontend/template")

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


@router.get("/googlelogin")
async def login(request: Request):
    # Generate a random state to prevent CSRF attacks
    state = secrets.token_urlsafe()
    request.session['oauth_state'] = state  # Store state in session

    # Redirect user to Google's OAuth authorization endpoint
    url = request.url_for('auth')  # The callback URL for OAuth
    return await oauth.google.authorize_redirect(request, url, state=state)

@router.get("/auth")
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
            user = userservice.check_google_email(db, email)
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
        access_token = auth.create_access_token(data={"sub": user.email},expires_delta=60)

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

