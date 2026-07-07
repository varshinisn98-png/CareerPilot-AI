from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database.models import User, Resume, ChatHistory
from app.database.schemas import ChatRequest, ChatResponse, ChatMessage
from app.auth.oauth import get_current_user
from app.services.rag_service import search_resume_index
from app.services.gemini_service import chat_with_resume
from app.utils.logger import logger

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
def ask_resume_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    RAG-powered chat: answer questions about the user's resume.
    Retrieves relevant resume chunks via FAISS and passes them to Gemini.
    """
    resume = db.query(Resume).filter(
        Resume.id == request.resume_id,
        Resume.user_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Resume text is empty.")

    # Retrieve relevant chunks via RAG
    chunks = search_resume_index(resume.id, request.message)
    if chunks:
        context = "\n\n---\n\n".join(chunks)
    else:
        # Fallback: use full resume text (truncated)
        context = resume.raw_text[:3000]

    # Fetch recent chat history
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id, ChatHistory.resume_id == resume.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(6)
        .all()
    )
    history_dicts = [{"role": h.role, "message": h.message} for h in reversed(history)]

    # Generate AI response
    try:
        reply = chat_with_resume(context, request.message, history_dicts)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    # Persist conversation turns
    db.add(ChatHistory(user_id=current_user.id, resume_id=resume.id, role="user", message=request.message))
    db.add(ChatHistory(user_id=current_user.id, resume_id=resume.id, role="assistant", message=reply))
    db.commit()

    logger.info(f"Chat reply generated for user {current_user.id}, resume {resume.id}.")
    return ChatResponse(reply=reply, sources=chunks[:2] if chunks else None)


@router.get("/history/{resume_id}", response_model=List[ChatMessage])
def get_chat_history(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return full chat history for a specific resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    return (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id, ChatHistory.resume_id == resume_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )


@router.delete("/history/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Clear all chat history for a specific resume."""
    db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id,
        ChatHistory.resume_id == resume_id,
    ).delete()
    db.commit()
