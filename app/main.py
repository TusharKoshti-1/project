# app/main.py
from fastapi import FastAPI 
from app.api.controllers import users_controller
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
from .config import CLIENT_ID,CLIENT_SECRET




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
           "http://127.0.0.1:5501"]

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

