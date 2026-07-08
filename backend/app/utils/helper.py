import os
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status
from app.utils.constants import ALLOWED_RESUME_EXTENSIONS, MAX_FILE_SIZE_MB


def generate_unique_filename(original_filename: str) -> str:
    """Generate a UUID-based filename while keeping the extension."""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"


def validate_pdf_file(file: UploadFile) -> None:
    """Validate that the uploaded file is a PDF within size limits."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only PDF files are allowed. Got: {ext}",
        )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks for embedding."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def truncate_text(text: str, max_chars: int = 4000) -> str:
    """Truncate text to a maximum character limit for LLM prompts."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "...[truncated]"
