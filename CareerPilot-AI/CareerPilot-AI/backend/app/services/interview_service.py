from typing import List, Dict, Any
from app.services.gemini_service import generate_interview_questions, _call_gemini
from app.utils.constants import VALID_QUESTION_TYPES
from app.utils.logger import logger


def get_interview_questions(resume_text: str, question_type: str, num_questions: int = 10) -> Dict[str, Any]:
    if question_type not in VALID_QUESTION_TYPES:
        raise ValueError(f"Invalid question type '{question_type}'. Must be one of: {VALID_QUESTION_TYPES}")
    logger.info(f"Generating {num_questions} {question_type} interview questions.")
    result = generate_interview_questions(resume_text, question_type, num_questions)
    questions: List[str] = result.get("questions", [])
    if not questions and "raw_response" in result:
        import re
        questions = re.findall(r'\d+[\.\)]\s+(.+)', result["raw_response"])
    return {
        "question_type": question_type,
        "questions": questions,
        "tips": result.get("tips", ""),
    }


def evaluate_answer(question: str, user_answer: str, question_type: str) -> Dict[str, Any]:
    """
    Evaluate a candidate's interview answer and provide detailed feedback.

    Returns scores and coaching tips on content, structure, and delivery.
    """
    type_context = {
        "hr": "behavioral/HR interview using STAR method (Situation, Task, Action, Result)",
        "technical": "technical interview requiring clear explanation of concepts and problem-solving",
        "project": "project-based interview requiring specific examples and lessons learned",
    }

    prompt = f"""You are an expert interview coach evaluating a candidate's answer.

INTERVIEW TYPE: {type_context.get(question_type, question_type)}

QUESTION: {question}

CANDIDATE'S ANSWER: {user_answer}

Evaluate this answer and respond in JSON format:
{{
  "overall_score": <number 1-10>,
  "content_score": <number 1-10>,
  "structure_score": <number 1-10>,
  "clarity_score": <number 1-10>,
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["specific improvement 1", "specific improvement 2"],
  "ideal_answer_structure": "Brief guide on how to structure a perfect answer to this question",
  "speaking_tips": ["tip on delivery 1", "tip on delivery 2", "tip on eye contact/pace etc"],
  "sample_better_answer": "A brief example of a stronger version of this answer (2-3 sentences)",
  "verdict": "one of: Excellent / Good / Needs Improvement / Practice More"
}}

Be encouraging but honest. Focus on helping them improve."""

    result = _call_gemini(prompt)

    import json, re
    clean = re.sub(r"```(?:json)?", "", result).replace("```", "").strip()
    try:
        return json.loads(clean)
    except Exception:
        return {
            "overall_score": 5,
            "content_score": 5,
            "structure_score": 5,
            "clarity_score": 5,
            "strengths": ["You attempted to answer the question"],
            "improvements": ["Try to be more specific with examples"],
            "ideal_answer_structure": "Use the STAR method: Situation → Task → Action → Result",
            "speaking_tips": ["Speak clearly and at a moderate pace", "Make eye contact"],
            "sample_better_answer": result[:300],
            "verdict": "Needs Improvement"
        }
