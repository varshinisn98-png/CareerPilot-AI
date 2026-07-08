import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

# Use an in-memory SQLite DB for tests
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
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
    """Reset DB before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_register_success():
    res = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "password123",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


def test_register_duplicate_email():
    payload = {"full_name": "User", "email": "dup@example.com", "password": "pass1234"}
    client.post("/api/auth/register", json=payload)
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_login_success():
    client.post("/api/auth/register", json={
        "full_name": "Login User",
        "email": "login@example.com",
        "password": "mypassword",
    })
    res = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "mypassword",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password():
    client.post("/api/auth/register", json={
        "full_name": "User", "email": "u@e.com", "password": "correct"
    })
    res = client.post("/api/auth/login", json={
        "email": "u@e.com", "password": "wrong"
    })
    assert res.status_code == 401


def test_get_profile_authenticated():
    client.post("/api/auth/register", json={
        "full_name": "Profile User", "email": "profile@e.com", "password": "pass1234"
    })
    login = client.post("/api/auth/login", json={
        "email": "profile@e.com", "password": "pass1234"
    })
    token = login.json()["access_token"]
    res = client.get("/api/user/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "profile@e.com"


def test_get_profile_unauthenticated():
    res = client.get("/api/user/me")
    assert res.status_code == 401
