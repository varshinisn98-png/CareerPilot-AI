from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── User Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── Resume Schemas ────────────────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ── ATS / Analysis Schemas ────────────────────────────────────────────────────

class ATSRequest(BaseModel):
    resume_id: int
    job_description: Optional[str] = None


class ATSResponse(BaseModel):
    ats_score: float
    extracted_skills: List[str]
    missing_skills: List[str]
    strengths: str
    weaknesses: str
    suggestions: str
    jd_match_percent: Optional[float] = None


# ── Interview Schemas ─────────────────────────────────────────────────────────

class InterviewRequest(BaseModel):
    resume_id: int
    question_type: str   # hr | technical | project
    num_questions: Optional[int] = 10


class InterviewResponse(BaseModel):
    question_type: str
    questions: List[str]


# ── Cover Letter Schemas ──────────────────────────────────────────────────────

class CoverLetterRequest(BaseModel):
    resume_id: int
    job_description: str


class CoverLetterResponse(BaseModel):
    content: str


# ── Chat Schemas ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    resume_id: int
    message: str


class ChatResponse(BaseModel):
    reply: str
    sources: Optional[List[str]] = None


class ChatMessage(BaseModel):
    role: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
