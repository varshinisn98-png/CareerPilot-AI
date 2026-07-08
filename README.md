# 🚀 CareerPilot AI: Smart Career Assistant

An AI-powered career assistant that helps students and job seekers build ATS-friendly resumes, prepare for interviews, and get personalized career guidance.

🔗 **Live Demo Link**: **[https://careerpilot-frontend-t0et.onrender.com](https://careerpilot-frontend-t0et.onrender.com)**

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 ATS Score | Resume scored against ATS criteria (0–100) with detailed qualitative tips |
| 🛠️ Skill Extraction | AI-powered skill detection and action-verb quality analysis from resume |
| 💼 JD Matching | Resume vs Job Description similarity scoring and gap suggestions |
| 💬 AI Resume Chat | RAG-powered Q&A directly chatting with your resume contents |
| 🎤 Interview Prep | AI-generated HR, Technical, and Project questions with grading |
| 📝 Cover Letter | Personalized cover letters from resume + JD |
| 📊 Dashboard | Visual summary of scores, skills, and suggestions |
| ⚙️ Key Swapper | Change Gemini API keys dynamically inside the app UI |

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, HTTPX |
| Backend | FastAPI, Uvicorn, Pydantic |
| Database | PostgreSQL + SQLAlchemy (Render) |
| Auth | JWT + native bcrypt |
| AI / LLM | Google Gemini API (gemini-2.5-flash) |
| Embeddings | Google Cloud Embeddings (text-embedding-004) |
| Vector DB | FAISS (Fast Approximate Nearest Neighbor) |
| PDF Parsing | PyMuPDF |
| Deployment | Docker + Render Cloud |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Google Gemini API key

### 1. Clone the Repository
```bash
git clone https://github.com/varshinisn98-png/CareerPilot-AI.git
cd CareerPilot-AI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

# Configure environment
# Create a .env file and add your GEMINI_API_KEY and DATABASE_URL
# Example DATABASE_URL: sqlite:///./test.db

# Start backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
Open a new terminal window:
```bash
cd frontend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

# Start frontend
streamlit run app.py
```

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
│   ├── components/        # Reusable UI components
│   ├── utils/             # Helpers
│   ├── views/             # Screen pages
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
venv\Scripts\activate
pytest ../tests -v
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
