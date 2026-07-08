from typing import List, Dict, Any
from app.services.gemini_service import generate_interview_questions, evaluate_interview_answer_with_gemini
from app.utils.constants import VALID_QUESTION_TYPES
from app.utils.logger import logger


def get_interview_questions(resume_text: str, question_type: str, num_questions: int = 10) -> Dict[str, Any]:
    """
    Generate interview questions for a given resume and question type.

    Args:
        resume_text: Full text of the candidate's resume.
        question_type: One of 'hr', 'technical', 'project'.
        num_questions: Number of questions to generate.

    Returns:
        Dict with 'question_type', 'questions' list, and optional 'tips'.

    Raises:
        ValueError: If question_type is invalid.
    """
    if question_type not in VALID_QUESTION_TYPES:
        raise ValueError(f"Invalid question type '{question_type}'. Must be one of: {VALID_QUESTION_TYPES}")

    logger.info(f"Generating {num_questions} {question_type} interview questions.")
    result = generate_interview_questions(resume_text, question_type, num_questions)

    # Normalise response structure
    questions: List[str] = result.get("questions", [])
    if not questions and "raw_response" in result:
        # Fallback: parse numbered list from raw text
        import re
        raw = result["raw_response"]
        questions = re.findall(r'\d+[\.\)]\s+(.+)', raw)

    return {
        "question_type": question_type,
        "questions": questions,
        "tips": result.get("tips", ""),
    }


def evaluate_answer(question: str, user_answer: str, question_type: str) -> Dict[str, Any]:
    """
    Evaluate a candidate's answer and provide feedback.

    Args:
        question: The interview question.
        user_answer: Candidate's response.
        question_type: Question type (hr, technical, project).

    Returns:
        Dict with 'score', 'strengths', 'weaknesses', 'suggestions', 'improved_answer'.
    """
    logger.info(f"Evaluating answer for question type '{question_type}'.")
    return evaluate_interview_answer_with_gemini(question, user_answer, question_type)

