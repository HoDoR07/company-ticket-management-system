from fastapi import FastAPI

from app.routers import users, tickets, technician, admin
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

app.include_router(users.router)
app.include_router(tickets.router)
app.include_router(technician.router)
app.include_router(admin.router)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "frontend" / "index.html")

@app.get("/login-page")
def login_page():
    return FileResponse(BASE_DIR/"frontend"/"login.html")