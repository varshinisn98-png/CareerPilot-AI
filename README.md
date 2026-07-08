# 🚀 CareerPilot AI

An AI-powered career assistant that helps students and job seekers build ATS-friendly resumes, prepare for interviews, and get personalized career guidance.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 ATS Score | Resume scored against ATS criteria (0–100) |
| 🛠️ Skill Extraction | NLP-powered skill detection from resume |
| 💼 JD Matching | Resume vs Job Description similarity scoring |
| 💬 AI Resume Chat | RAG-powered Q&A about your resume |
| 🎤 Interview Prep | AI-generated HR, Technical, and Project questions |
| 📝 Cover Letter | Personalized cover letters from resume + JD |
| 📊 Dashboard | Visual summary of scores, skills, and suggestions |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Auth | JWT + Passlib (bcrypt) |
| AI / LLM | Google Gemini API |
| NLP | spaCy, NLTK, Scikit-learn |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector DB | FAISS |
| PDF Parsing | PyMuPDF |
| Deployment | Docker + Docker Compose |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Google Gemini API key

### 1. Clone the repository
```bash
git clone https://github.com/yourname/CareerPilot-AI.git
cd CareerPilot-AI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Configure environment
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY and DATABASE_URL

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
pip install streamlit httpx

streamlit run app.py
```

### 4. Docker Compose (Recommended)
```bash
# Set your Gemini API key
set GEMINI_API_KEY=your-key-here    # Windows
# export GEMINI_API_KEY=your-key    # Mac/Linux

docker-compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📁 Project Structure

```
CareerPilot-AI/
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── auth/          # JWT + hashing
│   │   ├── database/      # Models, schemas, DB connection
│   │   ├── services/      # AI, PDF, RAG, embeddings
│   │   ├── utils/         # Helpers, constants, logger
│   │   ├── prompts/       # Gemini prompt templates
│   │   ├── config.py
│   │   └── main.py
│   ├── uploads/
│   ├── vector_db/
│   └── requirements.txt
├── frontend/
│   ├── pages/             # Streamlit pages
│   ├── components/        # Reusable UI components
│   ├── assets/            # CSS, logo
│   └── app.py
├── tests/
├── data/
├── docs/
└── docker-compose.yml
```

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 📖 API Documentation

Full API reference: [docs/api_documentation.md](docs/api_documentation.md)

Interactive Swagger UI: http://localhost:8000/docs

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing secret | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `ALGORITHM` | JWT algorithm (default: HS256) | ❌ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 60) | ❌ |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
