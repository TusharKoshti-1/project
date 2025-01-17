# app/main.py
from fastapi import FastAPI 
from app.api.controllers import users_controller
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.requests import Request



app = FastAPI()



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

@app.get("/employee", response_class=HTMLResponse)
async def read_employee(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("employee.html", {"request": request})


@app.get("/addEmployee", response_class=HTMLResponse)
async def add_employee(request: Request):
    # This will render the index.html template
    return templates.TemplateResponse("addEmployee.html", {"request": request})






