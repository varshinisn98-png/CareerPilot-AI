from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User, Resume, CoverLetter
from app.database.schemas import CoverLetterRequest, CoverLetterResponse
from app.auth.oauth import get_current_user
from app.services.gemini_service import generate_cover_letter
from app.utils.logger import logger

router = APIRouter()


@router.post("/generate", response_model=CoverLetterResponse)
def create_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized cover letter using the resume and job description."""
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resume text is empty.")

    try:
        content = generate_cover_letter(resume.raw_text, request.job_description)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    # Persist cover letter
    cover = CoverLetter(
        user_id=current_user.id,
        resume_id=resume.id,
        job_description=request.job_description,
        content=content,
    )
    db.add(cover)
    db.commit()

    logger.info(f"Cover letter generated for user {current_user.id}, resume {resume.id}.")
    return CoverLetterResponse(content=content)


@router.get("/history")
def get_cover_letter_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all previously generated cover letters."""
    letters = db.query(CoverLetter).filter(
        CoverLetter.user_id == current_user.id
    ).order_by(CoverLetter.created_at.desc()).limit(10).all()

    return [
        {"id": cl.id, "content": cl.content, "created_at": cl.created_at}
        for cl in letters
    ]
