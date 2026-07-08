import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.database.models import User, Resume
from app.database.schemas import ResumeResponse
from app.auth.oauth import get_current_user
from app.services.pdf_parser import parse_pdf
from app.services.rag_service import build_resume_index, delete_resume_index
from app.utils.helper import generate_unique_filename, validate_pdf_file
from app.config import settings
from app.utils.logger import logger

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload a PDF resume, parse it, and build a RAG index."""
    validate_pdf_file(file)

    unique_name = generate_unique_filename(file.filename)
    save_path = os.path.join(settings.upload_dir, unique_name)

    # Save file to disk
    async with aiofiles.open(save_path, "wb") as out_file:
        content = await file.read()
        if len(content) > settings.max_upload_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.max_upload_size_mb} MB.",
            )
        await out_file.write(content)

    # Parse PDF text
    try:
        raw_text = parse_pdf(save_path)
    except ValueError as e:
        os.remove(save_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # Save to DB
    resume = Resume(
        user_id=current_user.id,
        filename=file.filename,
        file_path=save_path,
        raw_text=raw_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    # Build FAISS vector index
    build_resume_index(resume.id, raw_text)
    logger.info(f"Resume uploaded: id={resume.id}, user={current_user.email}")
    return resume


@router.get("/history", response_model=List[ResumeResponse])
def get_resume_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a list of all resumes uploaded by the current user."""
    return db.query(Resume).filter(Resume.user_id == current_user.id).all()


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single resume by ID."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    return resume


@router.get("/{resume_id}/download")
def download_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download the original PDF file for a resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume or not os.path.exists(resume.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found.")
    return FileResponse(resume.file_path, media_type="application/pdf", filename=resume.filename)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume and its associated files."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")

    # Remove PDF and FAISS index
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    delete_resume_index(resume_id)

    db.delete(resume)
    db.commit()
