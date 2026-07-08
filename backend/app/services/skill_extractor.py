import re
from typing import List, Set
from app.utils.constants import COMMON_TECH_SKILLS
from app.utils.logger import logger

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    logger.warning("spaCy model 'en_core_web_sm' not found. Using keyword matching only.")


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract technical skills from resume text using keyword matching and NER.

    Args:
        text: Raw resume text.

    Returns:
        Deduplicated, sorted list of identified skills.
    """
    found_skills: Set[str] = set()
    text_lower = text.lower()

    # Keyword matching against known skill list
    for skill in COMMON_TECH_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill)

    # spaCy NER for additional entity extraction
    if SPACY_AVAILABLE:
        try:
            doc = nlp(text[:10000])  # Limit to avoid memory issues
            for ent in doc.ents:
                if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART"):
                    # Filter short tokens and common false positives
                    if len(ent.text) > 2 and ent.text.istitle():
                        found_skills.add(ent.text)
        except Exception as e:
            logger.warning(f"spaCy NER failed: {e}")

    logger.info(f"Extracted {len(found_skills)} skills from resume.")
    return sorted(found_skills)


def find_missing_skills(extracted_skills: List[str], job_description: str) -> List[str]:
    """
    Identify skills mentioned in the JD that are absent from the resume.

    Args:
        extracted_skills: Skills already found in the resume.
        job_description: Raw job description text.

    Returns:
        List of skills present in JD but missing from resume.
    """
    jd_lower = job_description.lower()
    extracted_lower = {s.lower() for s in extracted_skills}
    missing: List[str] = []

    for skill in COMMON_TECH_SKILLS:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, jd_lower) and skill.lower() not in extracted_lower:
            missing.append(skill)

    return sorted(missing)
