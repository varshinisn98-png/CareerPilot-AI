import pytest
from app.services.ats_service import calculate_ats_score, _check_resume_completeness
from app.services.skill_extractor import extract_skills_from_text, find_missing_skills


# ── Unit Tests: Skill Extractor ────────────────────────────────────────────────

def test_extract_known_skills():
    text = "I have experience with Python, FastAPI, PostgreSQL, Docker, and React."
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "FastAPI" in skills
    assert "Docker" in skills


def test_extract_skills_case_insensitive():
    text = "Proficient in python and DOCKER"
    skills = extract_skills_from_text(text)
    assert "Python" in skills
    assert "Docker" in skills


def test_find_missing_skills():
    resume_skills = ["Python", "FastAPI"]
    jd = "We require Docker, Kubernetes, and Python experience."
    missing = find_missing_skills(resume_skills, jd)
    assert "Docker" in missing
    assert "Kubernetes" in missing
    assert "Python" not in missing  # Already in resume


# ── Unit Tests: ATS Scoring ────────────────────────────────────────────────────

def test_ats_score_range():
    resume = (
        "John Doe | john@example.com | linkedin.com/in/john\n"
        "Education: B.Tech in CS from XYZ University\n"
        "Experience: Software Engineer at ABC Corp\n"
        "Skills: Python, FastAPI, PostgreSQL, Docker, React, Git\n"
        "Projects: Built an e-commerce platform using React and FastAPI"
    )
    result = calculate_ats_score(resume)
    assert 0 <= result["ats_score"] <= 100
    assert isinstance(result["extracted_skills"], list)


def test_ats_score_with_jd():
    resume = "Skills: Python, FastAPI, PostgreSQL, Docker"
    jd = "Looking for Python developer with FastAPI and Docker experience"
    result = calculate_ats_score(resume, jd)
    assert result["jd_match_percent"] > 0
    assert result["ats_score"] > 0


def test_completeness_score_full():
    resume = (
        "Contact: email@example.com | 555-1234\n"
        "Education: B.Sc Computer Science\n"
        "Experience: 3 years at Tech Corp\n"
        "Skills: Python, JavaScript, Docker\n"
        "Projects: Built a REST API"
    )
    score = _check_resume_completeness(resume)
    assert score == 100.0


def test_completeness_score_minimal():
    resume = "Just a name with nothing else."
    score = _check_resume_completeness(resume)
    assert score < 100.0


def test_ats_no_jd_returns_zero_match():
    result = calculate_ats_score("Python developer with experience")
    assert result["jd_match_percent"] == 0.0
    assert result["missing_skills"] == []
