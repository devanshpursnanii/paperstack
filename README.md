# PaperStack

<div align="center">

**AI-Powered Research Assistant with Citation-Grounded Multi-Paper RAG**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.1+-black.svg)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg)](https://reactjs.org/)

[Demo](#demo) • [Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## Overview

PaperStack is a full-stack AI system for academic research combining intelligent arXiv paper discovery with multi-paper RAG (Retrieval-Augmented Generation) chat. Every response is citation-backed, traceable to exact paper sources with page numbers.

### What Makes It Different

- **Dual-System Architecture**: Paper Brain (discovery) + Paper Chat (RAG)
- **Task-Aware Retrieval**: Automatic routing (QA/Summarize/Compare/Explain) with task-specific parameters
- **Paper-Aware MMR**: Ensures diverse coverage across multiple papers
- **Real-Time Metrics**: Token usage, latency tracking, chunk analysis per request
- **Token-Based Access**: Demo protection with browser-close state management

### Key Components

- **Paper Brain** — Agent-based semantic search with ChromaDB ranking (top 10 from 15 results)
- **Paper Chat** — Intelligent multi-paper RAG with hybrid retrieval (Vector + BM25)
- **Session Management** — In-memory sessions with quota limits, PostgreSQL metrics persistence
- **Metrics Dashboard** — Real-time visualization of tokens, latencies, and chunk usage

---

## Demo

**Access Token**: Contact via resume or project description

**Try It**:
1. Enter access token
2. Search: "attention mechanisms in transformers"
3. Load papers (select 2-3)
4. Ask: "Compare the attention mechanisms across these papers"
5. View real-time metrics in sidebar

---

## Features

### Paper Discovery (Paper Brain)
- ✅ Semantic query rewriting with LLM
- ✅ arXiv API integration (15 papers fetched)
- ✅ ChromaDB re-ranking (top 10 displayed)
- ✅ Title detection (bypasses rewrite for known papers)
- ✅ Agent-based refinement with tools

### Multi-Paper RAG (Paper Chat)
- ✅ Hybrid retrieval (Vector + BM25 fusion)
- ✅ Query enhancement (2 variations per query)
- ✅ LLM reranking (top 20 chunks)
- ✅ Paper-aware MMR diversity (λ=0.5-0.8 depending on task)
- ✅ Token compression (18K context limit)
- ✅ Inline citations [Paper Title, Page X]
- ✅ Task routing (4 strategies: QA/Summarize/Compare/Explain)

### Session & Metrics
- ✅ Session-based state management
- ✅ Per-request metrics (tokens, latency, chunks)
- ✅ Real-time dashboard updates
- ✅ Message persistence (localStorage)
- ✅ Quota enforcement (3 searches, 5 messages)

### Authentication & Security
- ✅ Token-based access control
- ✅ Bearer token authentication
- ✅ CORS configuration
- ✅ Browser-close state cleanup

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Google Gemini API Keys** ([Get free tier](https://aistudio.google.com/app/apikey))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/paperstack.git
cd paperstack

# 2. Install backend dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env: Add GOOGLE_API_KEY1 and GOOGLE_API_KEY2

# 5. Start servers
./start.sh
```

**Access**: http://localhost:3000  
**Token**: Set in .env (default: "welcometopaperstack1")

---

## Documentation

### Technical Deep Dives
- **[System Architecture](TECHNICAL.md)** - Complete system overview, data flows, component communication
- **[AI Module](ai/README.md)** - Paper Brain, RAG pipeline, retrieval strategies
- **[Backend API](backend/README.md)** - FastAPI endpoints, session management, auth
- **[Database Layer](backend/db/README.md)** - SQLite/PostgreSQL abstraction, schema, repository pattern
- **[Frontend](frontend/README.md)** - Next.js architecture, state management, components

### Setup Guides
- **[Authentication](AUTH_GUIDE.md)** - Token setup, browser state management
- **[Deployment](DEPLOYMENT.md)** - Production deployment guide
- **[Supabase Setup](SUPABASE_SETUP.md)** - PostgreSQL cloud database configuration

---

## Architecture

### System Stack

```
Frontend (Next.js 16 + React 19)
  ↓ REST API (Bearer Token Auth)
Backend (FastAPI + Python)
  ↓ Function Calls
AI Module (LlamaIndex + Gemini)
  ↓ External APIs
Google Gemini 2.5 Flash | arXiv API | ChromaDB
  ↓ Persistence
PostgreSQL/SQLite (Metrics)
```

### RAG Pipeline

```
User Query
  → Query Enhancement (2 variations)
  → Hybrid Retrieval (Vector + BM25)
  → LLM Reranking (Top 20)
  → Paper-Aware MMR (Diversity)
  → Token Compression (18K limit)
  → Citation Generation
  → Metrics Persistence
```

**Task Routing**: Automatic classification into QA (λ=0.8), Summarize (λ=0.6), Compare (λ=0.5), Explain (λ=0.7)

### Paper Brain Pipeline

```
User Query
  → Semantic Rewrite (LLM)
  → arXiv Search (15 papers)
  → ChromaDB Ranking (semantic similarity)
  → Top 10 Papers
  → Agent Loop (search_more | load_papers)
  → PDF Ingestion (pypdf, in-memory)
```

---

```bash
pip install -r requirements.txt
```

Or with virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Configure API Keys

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:

```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## Usage

### Option 1: Quick Start (Recommended)

Use the provided startup script to run both servers:

```bash
chmod +x start.sh
./start.sh
```

This will:
- ✓ Start FastAPI backend on `http://localhost:8000`
- ✓ Start Next.js frontend on `http://localhost:3000`
- ✓ Auto-reload on file changes

**Access the app**: Open [http://localhost:3000](http://localhost:3000)

Press `Ctrl+C` to stop both servers.

### Option 2: Run Individually

#### Terminal 1 - Backend

```bash
# From project root
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend

```bash
cd frontend
npm run dev
```

### Option 3: Production Build

#### Backend

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm run build
npm start
```

---

## Usage Guide

### 1. Search Papers
- Choose **Title Search** for exact paper titles (e.g., "Attention Is All You Need")
- Choose **Topic Search** for broader discovery (e.g., "transformer architectures")
- PaperBrain semantically ranks results and displays top 10 papers
- **Quota**: 3 searches per session

### 2. Load Papers
- Select papers using checkboxes
- Click **"Load Selected Papers"** to download and process PDFs
- Papers are parsed and indexed for retrieval

### 3. Chat with Papers
- Ask questions in PaperChat (e.g., "What is the attention mechanism?")
- Receive answers with **automatic citations** [Paper Title, Page X]
- Click citations to see exact source text
- **Quota**: 5 messages per session

### 4. Monitor Activity
- View loaded papers in **Session Activity** sidebar
- Track quota usage (searches remaining, messages remaining)
- Check cooldown timers when quotas exhausted

---

## API Documentation

Once running, access interactive API docs:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/session/create` | Create new session |
| `POST` | `/brain/search` | Search arXiv papers |
| `POST` | `/brain/load` | Load papers for RAG |
| `POST` | `/chat/message` | Query loaded papers |
| `GET` | `/session/{id}/info` | Get session info & logs |

---

## Project Structure

```
research-project/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── models.py            # Pydantic models
│   └── session.py           # Session management
├── frontend/
│   ├── app/                 # Next.js pages
│   ├── components/          # React components
│   ├── contexts/            # React contexts
│   └── lib/                 # API client
├── ai/
│   ├── web_interface.py     # Main RAG logic
│   ├── rag.py               # Multi-paper RAG engine
│   ├── query_engine.py      # Task-aware query routing
│   ├── quota_manager.py     # Quota & cooldown logic
│   └── logger.py            # Session logging
├── requirements.txt         # Python dependencies
├── start.sh                 # Startup script
└── .env.example            # Environment template
```

---

## Configuration

### Quota Limits

Edit `ai/quota_manager.py`:

```python
MAX_BRAIN_SEARCHES = 3      # Searches per session
MAX_CHAT_MESSAGES = 5       # Chat messages per session
USER_COOLDOWN_MINUTES = 15  # Cooldown after exhaustion
```

### RAG Parameters

Edit `ai/rag.py`:

```python
top_k_retrieve = 20         # Chunks to retrieve
top_k_rerank = 10           # Chunks after reranking
similarity_threshold = 0.1  # Minimum relevance score
```

### Session Retention

Edit `backend/main.py`:

```python
max_age_hours = 48          # Auto-cleanup old sessions
```

---

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt --force-reinstall
```

**"GOOGLE_API_KEY not found"**
- Ensure `.env` file exists in root directory
- Check key is properly formatted (no quotes, no spaces)

**Port 8000 already in use**
```bash
# Find process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Frontend Issues

**"Module not found"**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Port 3000 already in use**
```bash
# Find process on port 3000
lsof -ti:3000 | xargs kill -9
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

- **arXiv**: Research papers sourced from [arXiv.org](https://arxiv.org)
- **Google AI**: Powered by Gemini 2.5 Flash and text-embedding-004
- **LlamaIndex**: RAG framework
- **ChromaDB**: Vector database

---

## Developer

**Devansh Pursnani**  
Computer Science Engineering Student  
Applied AI • Language Models • Retrieval Systems

[![GitHub](https://img.shields.io/badge/GitHub-devanshpursnanii-181717?logo=github)](https://github.com/devanshpursnanii)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://www.linkedin.com/in/devansh-pursnani-946853231/)
[![Email](https://img.shields.io/badge/Email-devansh.pursnani23%40spit.ac.in-EA4335?logo=gmail)](mailto:devansh.pursnani23@spit.ac.in)

---

