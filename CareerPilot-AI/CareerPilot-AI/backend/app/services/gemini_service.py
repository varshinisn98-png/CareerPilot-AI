import json
import re
import os
from pathlib import Path
import google.generativeai as genai
from app.utils.logger import logger

# Load API key — check env var first, then .env file directly
_api_key = os.environ.get("GEMINI_API_KEY", "")

if not _api_key or _api_key == "your-gemini-api-key-here":
    # Try reading .env file directly
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                _api_key = line.split("=", 1)[1].strip()
                break

GEMINI_CONFIGURED = bool(_api_key and _api_key != "your-gemini-api-key-here")

if GEMINI_CONFIGURED:
    genai.configure(api_key=_api_key)
    _model = genai.GenerativeModel("gemini-1.5-flash")
    logger.info("Gemini AI configured successfully.")
else:
    _model = None
    logger.warning("Gemini API key not set. AI features will return placeholder responses.")


def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return raw text response."""
    if not GEMINI_CONFIGURED or _model is None:
        raise RuntimeError(
            "Gemini API key is not configured. Please add your GEMINI_API_KEY to backend/.env\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise RuntimeError(f"Gemini API error: {e}")


def _extract_json(text: str) -> dict:
    """Extract JSON from a Gemini response that may contain markdown fences."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"raw_response": text}


def analyze_resume_with_gemini(resume_text: str) -> dict:
    """Use Gemini to generate qualitative resume feedback."""
    prompt = f"""You are an expert resume reviewer. Analyze this resume and respond in JSON:
{{
  "strengths": "3-4 sentences about strong points",
  "weaknesses": "3-4 sentences about areas needing improvement",
  "suggestions": "5 specific bullet points to improve this resume",
  "formatting_feedback": "feedback on structure and readability",
  "career_recommendations": "2-3 suggested roles",
  "learning_roadmap": "top 5 skills to learn"
}}

RESUME:
{resume_text[:4000]}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def analyze_ats_with_gemini(resume_text: str, job_description: str) -> dict:
    """Use Gemini to perform ATS analysis against a JD."""
    prompt = f"""You are an ATS expert. Analyze this resume against the job description. Respond in JSON:
{{
  "ats_score": <number 0-100>,
  "jd_match_percent": <number 0-100>,
  "extracted_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strengths": "what makes this resume strong for this role",
  "weaknesses": "where this resume falls short",
  "suggestions": "specific improvements to increase ATS score"
}}

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def generate_interview_questions(resume_text: str, question_type: str, num_questions: int = 10) -> dict:
    """Generate interview questions tailored to the resume."""
    type_guide = {
        "hr": "behavioral questions using STAR method, cultural fit, motivation, teamwork",
        "technical": "role-specific technical questions based on skills in the resume",
        "project": "deep-dive questions about specific projects mentioned in the resume",
    }
    prompt = f"""You are an experienced interviewer. Generate {num_questions} {question_type} interview questions.
Type focus: {type_guide.get(question_type, question_type)}

RESUME:
{resume_text[:3000]}

Respond in JSON:
{{
  "question_type": "{question_type}",
  "questions": ["Question 1?", "Question 2?", ...],
  "tips": "brief tips for answering these questions"
}}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def generate_cover_letter(resume_text: str, job_description: str) -> str:
    """Generate a personalized cover letter."""
    prompt = f"""Write a professional, personalized cover letter (3-4 paragraphs, max 400 words).

Requirements:
- Strong opening mentioning the specific role
- Match top skills from resume to JD requirements  
- Highlight a specific achievement
- Professional closing with call-to-action
- Do NOT use generic phrases like "I am writing to express my interest"

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return only the cover letter text, no extra commentary."""
    return _call_gemini(prompt)


def chat_with_resume(resume_context: str, user_question: str, chat_history: list = None) -> str:
    """Answer a user question about their resume using RAG context."""
    history_text = ""
    if chat_history:
        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['message']}" for msg in chat_history[-6:]
        )

    prompt = f"""You are CareerPilot AI, a helpful career assistant. Answer based on the resume context.

RESUME CONTEXT:
{resume_context}

{f'CONVERSATION HISTORY:{chr(10)}{history_text}' if history_text else ''}

USER QUESTION: {user_question}

Give a helpful, specific, encouraging response. If the answer isn't in the context, say so honestly."""
    return _call_gemini(prompt)
