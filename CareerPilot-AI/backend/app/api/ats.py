from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.database.database import get_db
from app.database.models import User, Resume, ResumeAnalysis
from app.database.schemas import ATSRequest, ATSResponse
from app.auth.oauth import get_current_user
from app.services.ats_service import calculate_ats_score
from app.services.gemini_service import analyze_resume_with_gemini, analyze_ats_with_gemini
from app.utils.logger import logger

router = APIRouter()


@router.post("/analyze", response_model=ATSResponse)
def analyze_resume(
    request: ATSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform a full ATS analysis on a resume.
    Combines local scoring + Gemini AI feedback.
    """
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resume text is empty.")

    jd = request.job_description or ""

    # Local ATS scoring
    local_result = calculate_ats_score(resume.raw_text, jd)

    # Gemini AI analysis
    try:
        if jd.strip():
            ai_result = analyze_ats_with_gemini(resume.raw_text, jd)
        else:
            ai_result = analyze_resume_with_gemini(resume.raw_text)
    except Exception as e:
        logger.warning(f"Gemini analysis failed, using local only: {e}")
        ai_result = {}

    # Merge results (Gemini enriches local scores)
    ats_score = ai_result.get("ats_score", local_result["ats_score"])
    jd_match = ai_result.get("jd_match_percent", local_result["jd_match_percent"])
    extracted_skills = (
        ai_result.get("extracted_skills") or local_result["extracted_skills"]
    )
    missing_skills = (
        ai_result.get("missing_skills") or local_result["missing_skills"]
    )
    strengths = ai_result.get("strengths", "See suggestions below.")
    weaknesses = ai_result.get("weaknesses", "")
    suggestions = ai_result.get("suggestions", "")

    # Coerce lists/objects to markdown bullet strings
    if isinstance(strengths, list):
        strengths = "\n".join(f"- {s}" for s in strengths)
    elif not isinstance(strengths, str):
        strengths = str(strengths) if strengths is not None else ""

    if isinstance(weaknesses, list):
        weaknesses = "\n".join(f"- {s}" for s in weaknesses)
    elif not isinstance(weaknesses, str):
        weaknesses = str(weaknesses) if weaknesses is not None else ""

    if isinstance(suggestions, list):
        suggestions = "\n".join(f"- {s}" for s in suggestions)
    elif not isinstance(suggestions, str):
        suggestions = str(suggestions) if suggestions is not None else ""

    # Persist analysis
    existing = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume.id).first()
    analysis_data = dict(
        resume_id=resume.id,
        ats_score=ats_score,
        extracted_skills=json.dumps(extracted_skills),
        missing_skills=json.dumps(missing_skills),
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        jd_match_percent=jd_match,
        job_description=jd,
    )

    if existing:
        for key, value in analysis_data.items():
            setattr(existing, key, value)
    else:
        db.add(ResumeAnalysis(**analysis_data))
    db.commit()

    return ATSResponse(
        ats_score=ats_score,
        extracted_skills=extracted_skills,
        missing_skills=missing_skills,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        jd_match_percent=jd_match,
    )


@router.get("/result/{resume_id}", response_model=ATSResponse)
def get_ats_result(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a previously computed ATS analysis result."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == resume_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis found. Please run /api/ats/analyze first.",
        )

    return ATSResponse(
        ats_score=analysis.ats_score or 0,
        extracted_skills=json.loads(analysis.extracted_skills or "[]"),
        missing_skills=json.loads(analysis.missing_skills or "[]"),
        strengths=analysis.strengths or "",
        weaknesses=analysis.weaknesses or "",
        suggestions=analysis.suggestions or "",
        jd_match_percent=analysis.jd_match_percent,
    )
