# AI Tech Consultant (AI-TECH-CONSULTANT)

> A production-ready AI Technical Solutions Consultant ecosystem for the **Brilliant Directories** platform that automates customer service inquiries and transforms client meeting transcripts into structured project proposals and estimates using a RAG-powered backend.

---

## 🚀 Key Features & Capabilities

1. **Task 1: Knowledge Brain** – RAG-powered product knowledge base, web crawler, section-aware semantic chunker, ChromaDB vector store, and FastAPI backend (`http://localhost:8000`).
2. **Task 2: Inbox Agent** – Multi-channel customer inquiry triage, resolution drafting with Knowledge Brain citations, escalation routing, and interactive Web Dashboard (`http://localhost:3000`).
3. **Task 3: Meeting to Scope** – Discovery call transcript analysis, AI requirement extraction, and automated Scope of Work (SOW) generator with phased delivery and milestone pricing (`http://localhost:8001`).

---

## 📊 Quality Assurance & Automated Tests

All components are covered by end-to-end automated test suites (**39 / 39 Tests Passing, 100% Healthy**):
- **Task 1 (Knowledge Brain)**: 17 unit & integration tests passing (`pytest`)
- **Task 2 (Inbox Agent)**: 12 triage & API endpoint tests passing (`Node.js / Express`)
- **Task 3 (Meeting to Scope)**: 10 models, extractor & SOW generator tests passing (`pytest`)

Run all tests across the entire project with a single command:
```bash
python run_all_tests.py
```

---

## Unified Repository Architecture

```
AI-TECH-CONSULTANT/
├── .env.example                     # Unified environment template
├── .gitignore                       # Git ignore rules for Python, Node, ChromaDB, SQLite
├── README.md                        # Master repository documentation
├── run_all_tests.py                 # Unified test runner across all 3 tasks
│
├── task1-knowledge-brain/           # Task 1: RAG Knowledge System (Port 8000)
│   ├── app/                         # FastAPI REST API & Claude RAG Engine
│   │   ├── config.py                # Pydantic Settings
│   │   ├── database.py              # Async SQLite persistence (crawls, escalations, prompts)
│   │   ├── main.py                  # API routes (/query, /ingest, /escalations, /health)
│   │   ├── models.py                # Pydantic data schemas
│   │   ├── prompts.py               # System & Claude QA prompt templates
│   │   ├── rag_engine.py            # Retrieval & Claude synthesis pipeline
│   │   └── vector_store.py          # ChromaDB collection management
│   ├── data/                        # Verified Brilliant Directories seed knowledge
│   ├── ingestion/                   # Ingestion pipeline
│   │   ├── chunker.py               # Token-counted semantic chunker
│   │   ├── crawler.py               # Sitemap parser & rate-limited web crawler
│   │   ├── parser.py                # Structured HTML & screenshot context parser
│   │   └── pipeline.py              # End-to-end ingestion orchestrator
│   ├── tests/                       # Automated test suite (pytest)
│   ├── pyproject.toml               # Poetry/pip dependencies & pytest config
│   └── README.md                    # Task 1 documentation
│
├── task2-inbox-agent/               # Task 2: Autonomous Ticket Triage & Resolution (Port 3000)
│   ├── data/
│   │   └── seed_tickets.js          # Realistic Brilliant Directories support inquiries
│   ├── services/
│   │   ├── knowledge_brain.js       # Client integration with Task 1 API & fallback
│   │   └── triage.js                # AI classification, urgency scoring & draft engine
│   ├── public/                      # Web Dashboard Frontend
│   │   ├── css/style.css            # Dark-mode glassmorphic styling
│   │   ├── js/app.js                # Reactive state, simulation & approval workflows
│   │   └── index.html               # Semantic accessible HTML5 dashboard
│   ├── server.js                    # Express REST API & static server
│   ├── package.json                 # Node.js dependencies
│   └── README.md                    # Task 2 documentation
│
└── task3-meeting-to-scope/          # Task 3: Discovery Analysis & SOW Generator (Port 8001)
    ├── app/                         # FastAPI REST API & Scoping Engine
    │   ├── config.py                # Pydantic Settings
    │   ├── models.py                # Pydantic data schemas (Meeting, Analysis, Phase, SOW)
    │   ├── prompts.py               # Claude prompts for discovery analysis & scoping
    │   ├── extractor.py             # NLP & Claude requirement extraction engine
    │   ├── scope_generator.py       # Phased SOW, hours estimation & milestone calculator
    │   └── main.py                  # API routes (/api/meetings, /api/meetings/{id}/generate-sow)
    ├── data/
    │   └── seed_meetings.py         # Realistic discovery call transcripts (Healthcare, Contractors, Artisans)
    ├── static/                      # Web Dashboard Frontend
    │   ├── css/style.css            # Dark-mode glassmorphic styling
    │   └── js/app.js                # Reactive transcript reader & interactive SOW compiler
    ├── templates/
    │   └── index.html               # Semantic accessible HTML5 dashboard
    ├── tests/                       # Automated test suite (pytest)
    ├── pyproject.toml               # Poetry/pip dependencies & pytest config
    └── README.md                    # Task 3 documentation
```

---

## Quickstart

### 1. Environment Setup
```bash
copy .env.example .env
```
*(Optional: Add your `ANTHROPIC_API_KEY` for live Claude intelligence. Offline rule-based fallbacks are included out of the box).*

### 2. Task 1: Knowledge Brain (Port 8000)
```bash
cd task1-knowledge-brain
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- OpenAPI Documentation: `http://localhost:8000/docs`

### 3. Task 2: Inbox Agent (Port 3000)
```bash
cd task2-inbox-agent
npm install
npm start
```
- Interactive Dashboard: `http://localhost:3000`

### 4. Task 3: Meeting to Scope (Port 8001)
```bash
cd task3-meeting-to-scope
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
- Interactive Dashboard: `http://localhost:8001`
- OpenAPI Documentation: `http://localhost:8001/docs`

---

## Running Individual Test Suites

```bash
# Test Task 1: Knowledge Brain
cd task1-knowledge-brain
pytest tests/ -v

# Test Task 2: Inbox Agent
cd task2-inbox-agent
npm test

# Test Task 3: Meeting to Scope
cd task3-meeting-to-scope
pytest tests/ -v
```
