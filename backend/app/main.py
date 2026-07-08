from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database.database import engine, Base
from app.api import auth, resume, ats, interview, cover_letter, chat, user
from app.utils.logger import logger
from app.services.gemini_service import gemini_api_key_var

# Create DB tables
Base.metadata.create_all(bind=engine)

# Ensure upload and vector_db directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.vector_db_path, exist_ok=True)

app = FastAPI(
    title="CareerPilot AI",
    description="AI-powered career assistant for resume analysis, ATS scoring, interview prep, and more.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def extract_gemini_api_key(request, call_next):
    api_key = request.headers.get("X-Gemini-API-Key")
    token = gemini_api_key_var.set(api_key)
    try:
        response = await call_next(request)
        return response
    finally:
        gemini_api_key_var.reset(token)


# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(ats.router, prefix="/api/ats", tags=["ATS Analysis"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["Cover Letter"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Chat"])


@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "app": "CareerPilot AI", "version": "1.0.0"}


@app.on_event("startup")
async def startup_event():
    logger.info("CareerPilot AI backend started successfully.")
