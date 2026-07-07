import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.database.database import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test_resume.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def _get_auth_token(email="r@e.com", password="pass1234"):
    client.post("/api/auth/register", json={
        "full_name": "Resume User", "email": email, "password": password
    })
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def test_resume_history_empty():
    token = _get_auth_token()
    res = client.get("/api/resume/history", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json() == []


@patch("app.api.resume.parse_pdf", return_value="Sample resume text with Python and FastAPI skills.")
@patch("app.api.resume.build_resume_index", return_value=True)
def test_upload_resume(mock_index, mock_parse):
    token = _get_auth_token()
    # Create a minimal fake PDF bytes
    fake_pdf = b"%PDF-1.4 fake content"
    files = {"file": ("resume.pdf", io.BytesIO(fake_pdf), "application/pdf")}
    res = client.post(
        "/api/resume/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 201
    assert res.json()["filename"] == "resume.pdf"


def test_upload_non_pdf_rejected():
    token = _get_auth_token("x@e.com", "pass1234")
    files = {"file": ("resume.docx", io.BytesIO(b"fake"), "application/vnd.openxmlformats")}
    res = client.post(
        "/api/resume/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert res.status_code == 400


def test_get_nonexistent_resume():
    token = _get_auth_token("y@e.com", "pass1234")
    res = client.get("/api/resume/999", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
