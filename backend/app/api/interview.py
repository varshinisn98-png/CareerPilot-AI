import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import User, Resume, InterviewSession
from app.database.schemas import InterviewRequest, InterviewResponse
from app.auth.oauth import get_current_user
from app.services.interview_service import get_interview_questions, evaluate_answer
from app.utils.logger import logger

router = APIRouter()


class EvaluateRequest(BaseModel):
    question: str
    user_answer: str
    question_type: str = "hr"


@router.post("/generate", response_model=InterviewResponse)
def generate_questions(
    request: InterviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate AI-powered interview questions based on a resume."""
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resume text is empty.")

    try:
        result = get_interview_questions(resume.raw_text, request.question_type, request.num_questions)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    # Save session to DB
    session = InterviewSession(
        user_id=current_user.id,
        resume_id=resume.id,
        question_type=request.question_type,
        questions=json.dumps(result["questions"]),
    )
    db.add(session)
    db.commit()

    logger.info(f"Generated {len(result['questions'])} {request.question_type} questions for user {current_user.id}.")
    return InterviewResponse(
        question_type=result["question_type"],
        questions=result["questions"],
    )


@router.get("/history")
def get_interview_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return past interview question sessions for the current user."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id
    ).order_by(InterviewSession.created_at.desc()).limit(20).all()

    return [
        {
            "id": s.id,
            "question_type": s.question_type,
            "questions": json.loads(s.questions or "[]"),
            "created_at": s.created_at,
        }
        for s in sessions
    ]


@router.post("/evaluate")
def evaluate_interview_answer(
    request: EvaluateRequest,
    current_user: User = Depends(get_current_user),
):
    """Evaluate a candidate's answer and provide AI coaching feedback."""
    if not request.question.strip() or not request.user_answer.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Both question and answer are required.")
    try:
        result = evaluate_answer(request.question, request.user_answer, request.question_type)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
