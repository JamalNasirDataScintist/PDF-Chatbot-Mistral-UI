# 🧠 DocuMind AI — PDF Chatbot powered by Mistral AI

> AI/ML Engineer Assessment · AppLab · Deadline: 15/02/2026

A production-ready PDF chatbot that uses **RAG (Retrieval Augmented Generation)** with **Mistral AI** to provide intelligent, context-aware answers from uploaded documents.

---

## ✨ Features

- 📄 **PDF Upload & Processing** — drag-and-drop or click to upload
- 🤖 **Mistral AI Answers** — real AI-generated responses, not just text extraction
- 🔍 **Semantic Search** — finds the most relevant chunks via cosine similarity
- 📚 **Multi-document support** — upload multiple PDFs, ask across all of them
- 📌 **Source attribution** — shows which document section answered your question
- 🎨 **Professional dark UI** — modern, responsive interface
- 🐳 **Docker ready** — one command deployment

---

## 🏗️ Architecture

```
User Interface (HTML/CSS/JS — Dark theme)
           │
    Flask REST API
    ┌──────┴──────┐
    │             │
PDF Processor   Chatbot Service
(PyPDF2)        ┌──────────────┐
                │ Sentence     │  ← Embeddings (local)
                │ Transformers │
                │              │
                │ Mistral AI   │  ← Answer generation (API)
                │ mistral-small│
                └──────────────┘
                       │
               In-memory Vector Store
               (chunks + embeddings)
```

### RAG Pipeline
1. **Ingest** — PDF text extracted, split into 500-word overlapping chunks
2. **Embed** — Each chunk encoded via `all-MiniLM-L6-v2` (384-dim vectors)
3. **Retrieve** — Question embedding compared with all chunks via cosine similarity
4. **Generate** — Top-4 relevant chunks sent to Mistral AI with the question
5. **Respond** — Mistral generates a natural language answer with source attribution

---

## 🚀 Quick Start

### Option 1: Windows (double-click)
```
Double-click run.bat
```
Then open: http://localhost:5000

### Option 2: Manual
```bash
py -3.10 -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
python app.py
```

### Option 3: Docker
```bash
docker-compose up -d
```

---

## 📡 API Documentation

### POST `/api/upload`
Upload a PDF document.

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "success": true,
  "message": "document.pdf uploaded and processed successfully!",
  "document_id": "doc_0",
  "filename": "document.pdf",
  "pages": 5,
  "text_length": 8432
}
```

---

### POST `/api/chat`
Ask a question about uploaded documents.

**Request:**
```json
{ "question": "What are the main requirements?" }
```

**Response:**
```json
{
  "success": true,
  "question": "What are the main requirements?",
  "answer": "Based on the document, the main requirements are...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk": 3,
      "snippet": "The requirements include...",
      "relevance": 87.4
    }
  ],
  "confidence": "high",
  "model": "mistral-small-latest"
}
```

---

### GET `/api/documents`
List all uploaded documents.

```json
{
  "success": true,
  "documents": [
    { "id": "doc_0", "filename": "report.pdf", "chunks": 24 }
  ],
  "count": 1
}
```

---

### POST `/api/clear`
Clear all documents from knowledge base.

```json
{ "success": true, "message": "All documents cleared successfully" }
```

---

### GET `/api/health`
Health check.

```json
{
  "status": "healthy",
  "service": "PDF Chatbot API (Mistral AI)",
  "model": "mistral-small-latest",
  "documents_loaded": 2,
  "timestamp": "2026-02-15T10:30:00"
}
```

---

## ⚙️ Configuration (`.env`)

```env
MISTRAL_API_KEY=your_key_here
MISTRAL_MODEL=mistral-small-latest
MISTRAL_MAX_TOKENS=1024
MISTRAL_TEMPERATURE=0.3
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_CHUNKS=4
```

---

## 📁 Project Structure

```
pdf-chatbot/
├── app.py                  # Flask application & API endpoints
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container setup
├── docker-compose.yml      # Docker Compose config
├── run.bat                 # Windows one-click startup
├── test_api.py             # Automated API tests
├── .env                    # Environment variables
├── README.md               # Documentation
├── services/
│   ├── __init__.py
│   ├── pdf_processor.py    # PDF text extraction (PyPDF2)
│   └── chatbot.py          # RAG + Mistral AI engine
├── templates/
│   └── index.html          # Professional dark UI
└── uploads/                # Uploaded PDF files
```

---

## 🧪 Testing

```bash
# Run automated API tests
python test_api.py
```

---

## 🐳 Docker Deployment

```bash
# Build & start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔒 Security

- File type validation (PDF only)
- 32MB file size limit
- Secure filenames
- API key in environment variables
- CORS configured

---

**Built for AppLab AI/ML Engineer Assessment · 15/02/2026**
