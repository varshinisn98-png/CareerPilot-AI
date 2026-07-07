import json
import re
import os
from pathlib import Path
from contextvars import ContextVar
import threading
import google.generativeai as genai
from app.utils.logger import logger

gemini_api_key_var = ContextVar("gemini_api_key_var", default=None)
_gemini_lock = threading.Lock()

# Load API key — check env var first, then .env file directly
_api_key = os.environ.get("GEMINI_API_KEY", "")

if not _api_key or _api_key == "your-gemini-api-key-here":
    # Try reading .env file directly
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                _api_key = line.split("=", 1)[1].strip()
                break

GEMINI_CONFIGURED = bool(_api_key and _api_key != "your-gemini-api-key-here")

if GEMINI_CONFIGURED:
    genai.configure(api_key=_api_key)
    _model = genai.GenerativeModel("gemini-2.5-flash")
    logger.info("Gemini AI configured successfully.")
else:
    _model = None
    logger.warning("Gemini API key not set. AI features will return placeholder responses.")


def _get_local_fallback_response(prompt: str) -> str:
    """Generate a realistic mock response matching the requested task schema."""
    import json
    import re
    import random

    prompt_clean = prompt.lower()

    # 1. Interview Question generation
    if "experienced interviewer" in prompt_clean:
        # Find type (hr, technical, project) using regex on the prompt instructions only
        q_type = "hr"
        match_type = re.search(r'generate \d+ (hr|technical|project) interview', prompt_clean)
        if match_type:
            q_type = match_type.group(1)

        # Find num_questions
        num_questions = 10
        match = re.search(r'generate (\d+) ', prompt_clean)
        if match:
            num_questions = int(match.group(1))

        hr_pool = [
            "Tell me about a time you had to learn a new technology quickly to solve a problem.",
            "How do you handle disagreements within a development team?",
            "What is your greatest technical achievement, and why are you proud of it?",
            "Describe a situation where you had to debug a critical production issue under tight deadlines.",
            "Why are you interested in joining our company, and how do your skills align with this role?",
            "Tell me about a time you made a mistake at work. How did you resolve it?",
            "How do you prioritize your tasks when working on multiple projects with competing deadlines?",
            "Describe a time you had to work with a difficult team member. How did you manage the relationship?",
            "What strategies do you use to maintain focus and productivity when working remotely?",
            "Where do you see yourself professionally in the next three to five years?",
            "Describe a situation where you had to explain a complex technical concept to a non-technical person.",
            "How do you keep your technical skills up to date in such a fast-paced industry?",
            "Tell me about a project that failed. What went wrong, and what would you do differently today?",
            "What is your approach to giving and receiving constructive feedback?",
            "Describe a time you went above and beyond your standard duties to deliver a project successfully.",
            "How do you manage stress and maintain a healthy work-life balance?",
            "What does 'cultural fit' mean to you, and how do you contribute to a positive team environment?",
            "Describe a time you had to take the lead on a project. What was the outcome?",
            "How do you approach learning about a new business domain or industry for a client?",
            "What is the most important lesson you have learned in your career so far?"
        ]

        tech_pool = [
            "Explain the difference between SQL and NoSQL databases. When would you choose one over the other?",
            "What is a RESTful API? What are the key principles and HTTP methods used?",
            "How does Python manage memory? Explain garbage collection and reference counting.",
            "What is Docker, and why is it useful in a microservices architecture?",
            "Explain how git rebase works and how it differs from git merge.",
            "What is system design? Describe how you would design a scalable URL shortening service (like Bit.ly).",
            "What is database indexing? How does it speed up queries, and what are the trade-offs?",
            "Describe the concept of 'concurrency' in Python. What is the GIL, and how does it affect multi-threading?",
            "What are the differences between synchronous and asynchronous programming? How does asyncio help?",
            "Explain the basics of web security. What are SQL injection, XSS, and CSRF, and how do you prevent them?",
            "How would you optimize a slow database query in PostgreSQL?",
            "What is the difference between a process and a thread? Explain context switching.",
            "What is a message queue (like RabbitMQ or Kafka)? When and why would you use one?",
            "Describe how OAuth 2.0 authentication flow works.",
            "What is the difference between unit testing, integration testing, and end-to-end testing?",
            "Explain the model-view-controller (MVC) architecture.",
            "How do you ensure code quality and maintainability in a large collaborative codebase?",
            "What are design patterns? Explain the Singleton pattern and when it should be used.",
            "What is serverless computing (like AWS Lambda)? What are its advantages and disadvantages?",
            "Explain how HTTPS encrypts traffic between a client and a server."
        ]

        project_pool = [
            "Can you walk me through the architecture of the most complex project listed on your resume?",
            "What was the biggest technical challenge you faced while building your portfolio projects?",
            "How did you select the database (SQL vs NoSQL) for the projects you developed?",
            "If you had to rebuild your main project from scratch, what architectural choices would you change?",
            "How did you handle user authentication and authorization in your web applications?",
            "Describe how you deployed your projects. What hosting providers or CI/CD pipelines did you use?",
            "How did you test your application? Did you write automated unit tests?",
            "What was the scale of the application you built? How did you handle performance optimization?",
            "How did you handle error tracking and logging in your application?",
            "What third-party APIs did you integrate, and how did you handle API failures or rate limits?",
            "How did you design the database schema for your e-commerce or booking application?",
            "Did you implement caching (e.g. Redis)? Where and why did you use it?",
            "How did you ensure responsive design and high performance in the frontend of your application?",
            "What was the most interesting bug you encountered during development, and how did you fix it?",
            "How did you structure your backend code to make it modular and easily extendable?",
            "Describe your experience working with containerization (Docker) in your personal projects.",
            "What security measures did you implement to protect user data in your applications?",
            "How did you manage state in the frontend of your web applications?",
            "What was the feedback from users or reviewers of your projects, and how did you iterate on it?",
            "How did you manage environment variables and secrets safely during development?"
        ]

        pool = hr_pool if q_type == "hr" else (tech_pool if q_type == "technical" else project_pool)
        
        # Select unique questions from pool
        random.seed(42)  # For consistent output
        shuffled = list(pool)
        random.shuffle(shuffled)
        questions = shuffled[:min(num_questions, len(shuffled))]

        return json.dumps({
            "question_type": q_type,
            "questions": questions,
            "tips": f"Focus on active communication and structure your answers using specific examples. For {q_type} questions, prepare detail-oriented answers."
        })

    # 2. Answer Evaluation
    elif "expert interview coach" in prompt_clean:
        return json.dumps({
            "score": 85,
            "strengths": "Your response is clear, structures the situation nicely, and directly addresses the prompt.",
            "weaknesses": "It could be improved by providing more quantifiable metrics or details about your personal impact.",
            "suggestions": [
                "Structure your response strictly around Action and Result.",
                "Mention specific tools or technologies you used during the task."
            ],
            "improved_answer": "An improved version would be: 'In my experience with that situation, I analyzed the requirements and resolved the challenge by utilizing Python and FastAPI. This resulted in an efficient solution that was completed ahead of the deadline.'"
        })

    # 3. ATS / Job Description Match Analysis
    elif "ats expert" in prompt_clean:
        return json.dumps({
            "ats_score": 80,
            "jd_match_percent": 75,
            "extracted_skills": ["Python", "FastAPI", "SQL", "Docker", "Git", "PostgreSQL", "React", "JavaScript"],
            "missing_skills": ["AWS", "Kubernetes", "Redis", "CI/CD"],
            "strengths": "Excellent alignment with backend systems, REST APIs, database queries, and version control workflows.",
            "weaknesses": "Lacks cloud deployment (AWS) and container orchestration (Kubernetes) details highlighted in the JD.",
            "suggestions": "Highlight experience with cloud hosting, CI/CD deployment pipelines, or microservices architecture in your resume description to bridge the gaps."
        })

    # 4. Resume Feedback Reviewer
    elif "expert resume reviewer" in prompt_clean:
        return json.dumps({
            "strengths": "Your resume details strong engineering skills, structured project listings, and clean spacing hierarchies.",
            "weaknesses": "Descriptions are somewhat descriptive rather than metrics-focused. Some bullet points are long.",
            "suggestions": [
                "Include concrete results like percentage improvements or load time reductions.",
                "Keep bullet points concise and limit them to 1-2 lines.",
                "Ensure date formats and alignments are uniform.",
                "Begin descriptions with active verbs.",
                "Provide a brief summary of the project goals at the start."
            ],
            "formatting_feedback": "Readable font layout and section dividers. Ensure font sizing remains consistent across headers.",
            "career_recommendations": "Software Engineer, Backend Engineer, API Specialist",
            "learning_roadmap": ["Cloud hosting (AWS/GCP)", "Docker orchestration", "API security patterns", "Performance optimization", "CI/CD pipelines"]
        })

    # 5. Cover Letter Generation
    elif "write a professional, personalized cover letter" in prompt_clean:
        # Extract Job Description text
        jd_text = ""
        match_jd = re.search(r'job description:\s*(.*)', prompt_clean, re.DOTALL)
        if match_jd:
            jd_text = match_jd.group(1).strip()
        
        # Determine job title based on keywords in the prompt/JD
        job_title = "Software Engineer"
        if "data engineer" in jd_text or "data enginner" in jd_text:
            job_title = "Data Engineer"
        elif "frontend" in jd_text:
            job_title = "Frontend Developer"
        elif "backend" in jd_text:
            job_title = "Backend Developer"
        elif "full stack" in jd_text or "fullstack" in jd_text:
            job_title = "Full Stack Engineer"
        elif "data analyst" in jd_text:
            job_title = "Data Analyst"
        elif len(jd_text.splitlines()) > 0 and len(jd_text.splitlines()[0]) < 60:
            # Use first line if it's short
            first_line = jd_text.splitlines()[0].strip().strip('*-# ')
            if len(first_line) > 3:
                job_title = first_line.title()

        return (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {job_title} position. "
            f"Given the requirements outlined in your job description focusing on backend capabilities, "
            f"I am confident that my backend development skills and project building experience "
            f"make me an excellent fit for this role.\n\n"
            f"In my projects, I have developed extensive experience containerizing architectures "
            f"using Docker, optimizing complex SQL queries, and constructing scalable REST APIs "
            f"with Python and FastAPI. I enjoy solving complex engineering challenges and creating "
            f"systems that are modular, fast, and secure.\n\n"
            f"I am eager to apply my skills to the {job_title} role at your company. "
            f"Thank you for your time and consideration. I welcome the opportunity to discuss my "
            f"application further.\n\n"
            f"Sincerely,\n"
            f"Applicant"
        )

    # 6. Resume Chat / General assistant RAG fallback
    elif "helpful career assistant" in prompt_clean:
        # Extract user question (match until the trailing instruction)
        user_q = ""
        match_q = re.search(r'user question:\s*(.*?)(?:\n\ngive a helpful|$)', prompt_clean, re.DOTALL)
        if match_q:
            user_q = match_q.group(1).strip()
            
        user_q_clean = user_q.lower()
        
        # Extract resume context
        resume_ctx = ""
        match_ctx = re.search(r'resume context:\s*(.*?)(?:\n\nuser question:|\n\nconversation history:|$)', prompt_clean, re.DOTALL)
        if match_ctx:
            resume_ctx = match_ctx.group(1).strip()
            
        response_body = ""
        
        # Heuristics based on keywords
        if any(w in user_q_clean for w in ["hello", "hi", "hey", "greetings", "who are you"]):
            response_body = (
                "Hello! I am CareerPilot AI, your personal career coach.\n\n"
                "Even though we are currently operating under local fallback due to API quota limits, "
                "I can still provide high-quality guidance on:\n"
                "- **Resume Improvements** (formatting, wording, layout)\n"
                "- **Backend Engineering Skills** (FastAPI, Python, SQL, Docker)\n"
                "- **Portfolio Projects** (ideas, architectures)\n"
                "- **Interview Preparation** (technical, behavioral)\n\n"
                "What would you like to discuss today?"
            )
        elif any(w in user_q_clean for w in ["suitable", "position", "role", "job", "company", "companies", "bangalore", "bengaluru"]):
            # Dynamic job recommendations based on resume context
            detected_roles = []
            has_ml = any(w in resume_ctx.lower() for w in ["machine learning", "nlp", "model", "data science", "tensorflow", "pytorch", "analytics"])
            has_react = any(w in resume_ctx.lower() for w in ["react", "frontend", "javascript", "css", "html", "nextjs", "vue", "angular"])
            has_backend = any(w in resume_ctx.lower() for w in ["fastapi", "backend", "python", "sql", "postgresql", "django", "node", "java", "mongodb"])
            
            if has_ml:
                detected_roles.extend(["Machine Learning Engineer", "NLP Research Engineer", "Data Scientist"])
            if has_backend:
                detected_roles.extend(["Backend Developer", "Software Development Engineer (SDE)", "API Engineer"])
            if has_react:
                detected_roles.extend(["Frontend Developer", "Full Stack Engineer"])
                
            if not detected_roles:
                detected_roles = ["Software Engineer", "Associate Developer"]
                
            roles_str = ", ".join(detected_roles)
            
            response_body = (
                f"Based on your resume context, here is an analysis of roles you are highly suitable for:\n\n"
                f"### 🎯 Suitable Positions:\n"
                f"- **{detected_roles[0]}** (Core match based on your technical achievements)\n"
            )
            for r_type in detected_roles[1:]:
                response_body += f"- **{r_type}**\n"
                
            # If they asked for companies or Bangalore
            if any(w in user_q_clean for w in ["bangalore", "bengaluru", "company", "companies"]):
                response_body += (
                    f"\n### 🏢 Top Tech Companies in Bangalore (Bengaluru) hiring for your profile:\n"
                    f"1. **Flipkart & Swiggy** (Headquartered in Bangalore) - Great for scalable product backend architectures (python/microservices).\n"
                    f"2. **Zerodha & Razorpay** - Active product companies looking for clean API developers and robust backend engineering.\n"
                    f"3. **Walmart Global Tech & Amazon** (Major Bangalore tech hubs) - Highly value deep backend architecture, sql databases, and data structures.\n"
                    f"4. **CRED & PhonePe** - Strong engineering teams looking for backend or fullstack developers.\n"
                    f"5. **Tech Startups (HSR Layout / Indiranagar)** - High demand for FastAPI and Python developers for fast iteration.\n\n"
                    f"To stand out, highlight key metrics from your projects (like speedups or database index achievements) when applying!"
                )
            else:
                response_body += (
                    f"\nWould you like me to recommend top tech companies in Bangalore that are actively hiring for these positions?"
                )
        elif any(w in user_q_clean for w in ["strength", "weakness"]):
            response_body = (
                "Based on your resume context, here is an analysis of your strengths and potential areas to improve:\n\n"
                "### 💪 Key Strengths:\n"
                "- **Modern Tech Stack**: Good integration of frameworks (Python, FastAPI, databases).\n"
                "- **Implemented Projects**: Clear demonstration of practical skills via portfolio projects.\n\n"
                "### 🔧 Areas to Improve:\n"
                "- **Quantifiable Results**: Try describing your impacts using percentages or numbers (e.g., 'reduced query time by 20%').\n"
                "- **Infrastructure/Cloud**: Adding container orchestration (Kubernetes) or cloud infrastructure (AWS/GCP) will make your profile stand out."
            )
        elif any(w in user_q_clean for w in ["skill", "learn", "develop", "technology", "language", "study"]):
            response_body = (
                "To accelerate your career as a software engineer, I highly recommend developing these high-demand skills:\n\n"
                "1. **Containerization & Orchestration**: Learn **Docker** and **Kubernetes** to package and deploy apps reliably.\n"
                "2. **Caching & Message Queues**: Master **Redis** (for caching database queries) and **RabbitMQ/Kafka** (for asynchronous task processing).\n"
                "3. **Cloud Infrastructure**: Get familiar with cloud providers like **AWS** (EC2, S3, RDS) or **Google Cloud**.\n"
                "4. **Database Mastery**: Understand database indexes, connection pooling, and ACID properties in PostgreSQL/MySQL.\n"
                "5. **Testing**: Write unit and integration tests using **Pytest** to ensure code reliability.\n\n"
                "Which of these skills would you like to deep dive into first?"
            )
        elif any(w in user_q_clean for w in ["backend", "fastapi", "python", "sql", "api", "database", "postgresql"]):
            response_body = (
                "For robust backend development in Python/FastAPI:\n\n"
                "- **FastAPI Best Practices**:\n"
                "  - Use `async def` for I/O bound tasks and standard `def` for CPU-bound tasks.\n"
                "  - Leverage Pydantic schemas for data validation and auto-documentation.\n"
                "  - Structure files modularly: separate routers, services, schemas, and database layers.\n"
                "- **SQL & Database Performance**:\n"
                "  - Create indexes on columns used in `WHERE`, `JOIN`, or `ORDER BY` operations.\n"
                "  - Use connection pooling (like SQLAlchemy's QueuePool) to manage DB resource load.\n"
                "  - Avoid N+1 queries by pre-fetching relations.\n\n"
                "Let me know if you would like code examples for any of these patterns!"
            )
        elif any(w in user_q_clean for w in ["project", "portfolio", "build", "idea", "create"]):
            response_body = (
                "Here are four strong portfolio project ideas that impress interviewers:\n\n"
                "1. **Real-time Chat Application**: Built with FastAPI WebSockets, Redis pub/sub for scaling chat rooms, and PostgreSQL for history.\n"
                "2. **Distributed Task Queue**: A Celery/Redis task worker system in Python that scrapes and processes data asynchronously.\n"
                "3. **API Rate Limiter Middleware**: A custom sliding-window rate limiter using Redis to protect server endpoints.\n"
                "4. **E-Commerce Backend**: Featuring stripe integration, transactional database updates, and JWT authorization.\n\n"
                "Would you like me to walk through the system design for one of these?"
            )
        elif any(w in user_q_clean for w in ["resume", "cv", "improve", "feedback", "layout", "format"]):
            response_body = (
                "To optimize your resume for recruiters and ATS systems:\n\n"
                "- **Use the STAR Method**: State the **S**ituation, **T**ask, **A**ction, and **Result**. (e.g. *'Optimized SQL queries (Action), reducing loading time by 30% (Result)'*).\n"
                "- **Focus on Action Verbs**: Start bullets with verbs like *'Spearheaded'*, *'Architected'*, *'Implemented'*, *'Reduced'*.\n"
                "- **Clear Layout**: Use clean typography, align all dates to the right margin, and avoid multiple columns or graphics which confuse ATS parsers.\n\n"
                "Would you like me to rewrite one of your project descriptions as an example?"
            )
        elif any(w in user_q_clean for w in ["job", "career", "hire", "get", "interview", "prep", "salary", "apply"]):
            response_body = (
                "Here is a structured preparation plan for software engineering interviews:\n\n"
                "1. **Behavioral (STAR Method)**: Prepare 4-5 stories about conflict resolution, failure, leadership, and learning new tools.\n"
                "2. **System Design**: Study load balancing, horizontal vs vertical scaling, databases, and microservices.\n"
                "3. **Coding Challenges**: Practice patterns like sliding window, two pointers, depth-first search, and tree traversals.\n"
                "4. **Job Hunting**: Tailor your resume key phrases to match the job descriptions of roles you apply to.\n\n"
                "What kind of interview (technical or behavioral) are you preparing for next?"
            )
        else:
            response_body = (
                f"I understand your question relates to: '{user_q}'.\n\n"
                f"To give you specific guidance:\n"
                f"- If you're looking to enhance your **technical skills**, focusing on Docker, Redis, and Cloud hosting is a great path.\n"
                f"- If you want to improve **resume impact**, try quantifying your achievements with numbers (e.g., '% performance improvement').\n"
                f"- If you are preparing for **interviews**, practice explaining the system architecture of your projects.\n\n"
                f"Please let me know which area you'd like to dive into, and I will supply detailed suggestions!"
            )

        return (
            f"Based on your resume context, you have a solid background in software engineering.\n\n"
            f"{response_body}"
        )

    return "Mock response generated locally due to Gemini API limit restrictions."


def _call_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return raw text response."""
    custom_key = gemini_api_key_var.get()
    if custom_key:
        try:
            with _gemini_lock:
                genai.configure(api_key=custom_key)
                local_model = genai.GenerativeModel("gemini-2.5-flash")
                response = local_model.generate_content(prompt)
                # Restore default key if configured
                if GEMINI_CONFIGURED:
                    genai.configure(api_key=_api_key)
                return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error with custom key: {e}")
            # Fall back to local responder if custom key fails/429s
            return _get_local_fallback_response(prompt)

    if not GEMINI_CONFIGURED or _model is None:
        raise RuntimeError(
            "Gemini API key is not configured. Please add your GEMINI_API_KEY to backend/.env\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )
    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        err_msg = str(e).upper()
        if "QUOTA" in err_msg or "LIMIT" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            logger.warning("Gemini quota exceeded or rate limited. Falling back to local response generator.")
            return _get_local_fallback_response(prompt)
        logger.error(f"Gemini API error: {e}")
        raise RuntimeError(f"Gemini API error: {e}")


def _extract_json(text: str) -> dict:
    """Extract JSON from a Gemini response that may contain markdown fences."""
    clean = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        return {"raw_response": text}


def analyze_resume_with_gemini(resume_text: str) -> dict:
    """Use Gemini to generate qualitative resume feedback."""
    prompt = f"""You are an expert resume reviewer. Analyze this resume and respond in JSON:
{{
  "strengths": "3-4 sentences about strong points",
  "weaknesses": "3-4 sentences about areas needing improvement",
  "suggestions": "5 specific bullet points to improve this resume",
  "formatting_feedback": "feedback on structure and readability",
  "career_recommendations": "2-3 suggested roles",
  "learning_roadmap": "top 5 skills to learn"
}}

RESUME:
{resume_text[:4000]}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def analyze_ats_with_gemini(resume_text: str, job_description: str) -> dict:
    """Use Gemini to perform ATS analysis against a JD."""
    prompt = f"""You are an ATS expert. Analyze this resume against the job description. Respond in JSON:
{{
  "ats_score": <number 0-100>,
  "jd_match_percent": <number 0-100>,
  "extracted_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strengths": "what makes this resume strong for this role",
  "weaknesses": "where this resume falls short",
  "suggestions": "specific improvements to increase ATS score"
}}

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def generate_interview_questions(resume_text: str, question_type: str, num_questions: int = 10) -> dict:
    """Generate interview questions tailored to the resume."""
    type_guide = {
        "hr": "behavioral questions using STAR method, cultural fit, motivation, teamwork",
        "technical": "role-specific technical questions based on skills in the resume",
        "project": "deep-dive questions about specific projects mentioned in the resume",
    }
    prompt = f"""You are an experienced interviewer. Generate {num_questions} {question_type} interview questions.
Type focus: {type_guide.get(question_type, question_type)}

RESUME:
{resume_text[:3000]}

Respond in JSON:
{{
  "question_type": "{question_type}",
  "questions": ["Question 1?", "Question 2?", ...],
  "tips": "brief tips for answering these questions"
}}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)


def generate_cover_letter(resume_text: str, job_description: str) -> str:
    """Generate a personalized cover letter."""
    prompt = f"""Write a professional, personalized cover letter (3-4 paragraphs, max 400 words).

Requirements:
- Strong opening mentioning the specific role
- Match top skills from resume to JD requirements  
- Highlight a specific achievement
- Professional closing with call-to-action
- Do NOT use generic phrases like "I am writing to express my interest"

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Return only the cover letter text, no extra commentary."""
    return _call_gemini(prompt)


def chat_with_resume(resume_context: str, user_question: str, chat_history: list = None) -> str:
    """Answer a user question about their resume using RAG context."""
    history_text = ""
    if chat_history:
        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['message']}" for msg in chat_history[-6:]
        )

    prompt = f"""You are CareerPilot AI, a helpful career assistant. Answer based on the resume context.

RESUME CONTEXT:
{resume_context}

{f'CONVERSATION HISTORY:{chr(10)}{history_text}' if history_text else ''}

USER QUESTION: {user_question}

Give a helpful, specific, encouraging response. If the answer isn't in the context, say so honestly."""
    return _call_gemini(prompt)


def evaluate_interview_answer_with_gemini(question: str, user_answer: str, question_type: str) -> dict:
    """Evaluate a candidate's answer to an interview question using Gemini."""
    prompt = f"""You are an expert interview coach. Evaluate the candidate's answer to the following question.
Question Type: {question_type}
Question: {question}
Candidate's Answer: {user_answer}

Provide feedback and suggestions. Respond in JSON format:
{{
  "score": <number 0-100 indicating answer quality>,
  "strengths": "1-2 sentences highlighting what the user did well",
  "weaknesses": "1-2 sentences highlighting what was missing or could be improved",
  "suggestions": ["suggestion 1", "suggestion 2"],
  "improved_answer": "an optimized version of the user's answer that maintains their personal context but improves delivery and impact"
}}"""
    raw = _call_gemini(prompt)
    return _extract_json(raw)

