# app/main.py
from fastapi import Depends, FastAPI, HTTPException
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
from .config import CLIENT_ID,CLIENT_SECRET, get_db

app = FastAPI()
app.add_middleware(SessionMiddleware,secret_key="add any string...")

oauth = OAuth()
oauth.register(
    name ='google',
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration",
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    client_kwargs={
        'scope':'email openid profile',
        'redirect_url':'http://localhost:8000/auth/callback'
    }
)




# Serving static files (like CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="app/frontend/static"), name="static")

# Setting up the templates folder for Jinja2
templates = Jinja2Templates(directory="app/frontend/template")


origins = ["http://127.0.0.1:5500",
           "http://127.0.0.1:5501",
           "http://127.0.0.1:8000"]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(users_controller.router, prefix="/users")

@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def read_home(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/employee", response_class=HTMLResponse)
async def read_employee(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("employee.html", {"request": request})


@app.get("/add-employee", response_class=HTMLResponse)
async def add_employee(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("addEmployee.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    url = request.url_for('auth')
    return await oauth.google.authorize_redirect(request,url)

@app.get('/auth')
async def auth(request: Request, db: Session = Depends(get_db)):
    try:
        # Get the token from Google's OAuth
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        # Render error page on OAuth failure
        return templates.TemplateResponse(
            name='error.html',
            context={'request': request, 'error': e.error}
        )

    # Get userinfo from the token
    user_info = token.get('userinfo')

    if user_info:
        email = user_info.get('email')

        # Use the new function to check if the email exists in the database
        try:
            user = check_google_email(db, email)
            print(email + 'login succesful')
        except HTTPException as e:
            print(email + 'not in database')
            # If the user doesn't exist, render an error template
            return templates.TemplateResponse(
                name='error.html',
                context={'request': request, 'error': e.detail}
            )

        # Store user data in the session
        request.session['user'] = {
            "email": user.email,
            "role_id": user.role_id
        }

        # Render the dashboard with user data
        return templates.TemplateResponse(
            name='dashboard.html',
            context={'request': request, 'user': request.session['user']}
        )

    # Render error if no userinfo is found
    return templates.TemplateResponse(
        name='error.html',
        context={'request': request, 'error': "Failed to retrieve user information from Google."}
    )
