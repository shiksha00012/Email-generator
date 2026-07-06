from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.database import init_db, engine
from app.routers import emails, history
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify MySQL connection before accepting traffic
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as e:
        raise RuntimeError(
            f"Cannot connect to MySQL: {e}\n"
            "Check DATABASE_URL in your .env file."
        )
    init_db()   # CREATE TABLE IF NOT EXISTS for all models
    yield


app = FastAPI(
    title="AI Email Assistant",
    description="Generate, reply, convert tone, and summarize emails using Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(emails.router,  prefix="/api/emails",  tags=["emails"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """Check server + DB connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "service": "AI Email Assistant", "database": db_status}
