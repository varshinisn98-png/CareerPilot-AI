# CareerPilot AI — API Documentation

Base URL: `http://localhost:8000`  
Interactive Docs: `http://localhost:8000/docs`

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 🔐 Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and get JWT token |

**Register** `POST /api/auth/register`
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "password": "securepassword"
}
```

**Login** `POST /api/auth/login`
```json
{
  "email": "jane@example.com",
  "password": "securepassword"
}
```
Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

---

### 👤 User

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/me` | Get current user profile |
| PUT | `/api/user/me` | Update user profile |
| DELETE | `/api/user/me` | Delete account |

---

### 📄 Resume

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/resume/upload` | Upload PDF resume (multipart/form-data) |
| GET | `/api/resume/history` | List all resumes |
| GET | `/api/resume/{id}` | Get a specific resume |
| GET | `/api/resume/{id}/download` | Download PDF |
| DELETE | `/api/resume/{id}` | Delete resume |

---

### 🤖 ATS Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ats/analyze` | Run full ATS analysis |
| GET | `/api/ats/result/{resume_id}` | Get cached analysis result |

**Request** `POST /api/ats/analyze`
```json
{
  "resume_id": 1,
  "job_description": "Optional job description text..."
}
```

**Response**
```json
{
  "ats_score": 82.5,
  "extracted_skills": ["Python", "FastAPI", "Docker"],
  "missing_skills": ["Kubernetes", "AWS"],
  "strengths": "Strong technical background...",
  "weaknesses": "Limited cloud experience...",
  "suggestions": "Add cloud certifications...",
  "jd_match_percent": 74.3
}
```

---

### 🎤 Interview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/generate` | Generate interview questions |
| GET | `/api/interview/history` | Get past sessions |

**Request** `POST /api/interview/generate`
```json
{
  "resume_id": 1,
  "question_type": "hr"
}
```
`question_type`: `hr` | `technical` | `project`

---

### 📝 Cover Letter

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cover-letter/generate` | Generate cover letter |
| GET | `/api/cover-letter/history` | Get past cover letters |

**Request** `POST /api/cover-letter/generate`
```json
{
  "resume_id": 1,
  "job_description": "We are looking for a Python developer..."
}
```

---

### 💬 Chat (RAG)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/ask` | Ask a question about your resume |
| GET | `/api/chat/history/{resume_id}` | Get chat history |
| DELETE | `/api/chat/history/{resume_id}` | Clear chat history |

**Request** `POST /api/chat/ask`
```json
{
  "resume_id": 1,
  "message": "What are my key strengths?"
}
```

**Response**
```json
{
  "reply": "Based on your resume, your key strengths are...",
  "sources": ["chunk1...", "chunk2..."]
}
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad Request — invalid input |
| 401 | Unauthorized — missing or invalid token |
| 403 | Forbidden — insufficient permissions |
| 404 | Not Found — resource doesn't exist |
| 413 | Payload Too Large — file exceeds size limit |
| 422 | Unprocessable Entity — validation error |
| 503 | Service Unavailable — AI service error |
