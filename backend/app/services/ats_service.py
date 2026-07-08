import re
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.skill_extractor import extract_skills_from_text, find_missing_skills
from app.utils.logger import logger


def calculate_ats_score(resume_text: str, job_description: str = "") -> Dict[str, Any]:
    """
    Calculate an ATS compatibility score for a resume.

    Scoring breakdown:
      - Skills coverage:   40%
      - JD keyword match:  30% (0 if no JD provided)
      - Resume completeness: 30%

    Args:
        resume_text: Full text of the resume.
        job_description: Optional job description for JD-based scoring.

    Returns:
        Dictionary with ats_score, jd_match_percent, extracted_skills, missing_skills.
    """
    extracted_skills = extract_skills_from_text(resume_text)
    missing_skills: List[str] = []
    jd_match_percent: float = 0.0

    # ── JD similarity using TF-IDF cosine ─────────────────────────────────────
    if job_description.strip():
        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            jd_match_percent = round(float(similarity) * 100, 2)
        except Exception as e:
            logger.warning(f"TF-IDF similarity failed: {e}")
            jd_match_percent = 0.0

        missing_skills = find_missing_skills(extracted_skills, job_description)

    # ── Completeness check ─────────────────────────────────────────────────────
    completeness_score = _check_resume_completeness(resume_text)

    # ── Skills coverage score ──────────────────────────────────────────────────
    skill_score = min(len(extracted_skills) * 4, 100)  # 4 pts per skill, max 100

    # ── Weighted ATS score ─────────────────────────────────────────────────────
    if job_description.strip():
        ats_score = (
            skill_score * 0.40
            + jd_match_percent * 0.30
            + completeness_score * 0.30
        )
    else:
        ats_score = skill_score * 0.50 + completeness_score * 0.50

    ats_score = round(min(ats_score, 100), 2)

    logger.info(f"ATS Score: {ats_score} | JD Match: {jd_match_percent}%")
    return {
        "ats_score": ats_score,
        "jd_match_percent": jd_match_percent,
        "extracted_skills": extracted_skills,
        "missing_skills": missing_skills,
        "completeness_score": completeness_score,
    }


def _check_resume_completeness(text: str) -> float:
    """Score resume completeness based on presence of key sections (0–100)."""
    sections = {
        "contact": r'(email|phone|linkedin|github|@)',
        "education": r'\b(education|university|college|degree|bachelor|master|b\.tech|m\.tech)\b',
        "experience": r'\b(experience|work|internship|employment|company)\b',
        "skills": r'\b(skills|technologies|tools|proficient)\b',
        "projects": r'\b(projects|portfolio|built|developed|created)\b',
    }
    score = 0
    text_lower = text.lower()
    for section, pattern in sections.items():
        if re.search(pattern, text_lower):
            score += 20  # 20 pts per section, 5 sections = 100
    return float(score)
