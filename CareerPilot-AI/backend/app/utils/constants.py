# ATS scoring weights
ATS_WEIGHT_SKILLS = 0.40
ATS_WEIGHT_KEYWORDS = 0.30
ATS_WEIGHT_FORMAT = 0.20
ATS_WEIGHT_EXPERIENCE = 0.10

# Supported file types
ALLOWED_RESUME_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_MB = 10

# Interview question types
QUESTION_TYPE_HR = "hr"
QUESTION_TYPE_TECHNICAL = "technical"
QUESTION_TYPE_PROJECT = "project"
VALID_QUESTION_TYPES = {QUESTION_TYPE_HR, QUESTION_TYPE_TECHNICAL, QUESTION_TYPE_PROJECT}

# RAG
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 4

# Common tech skills for gap analysis
COMMON_TECH_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
    "React", "Angular", "Vue.js", "Node.js", "FastAPI", "Django", "Flask",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "CI/CD",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
    "Git", "Linux", "REST API", "GraphQL", "Microservices",
    "Data Structures", "Algorithms", "System Design",
]

# Section headers for resume parsing
RESUME_SECTION_HEADERS = [
    "education", "experience", "work experience", "skills", "projects",
    "certifications", "achievements", "summary", "objective",
    "publications", "awards", "languages", "hobbies", "references",
]
