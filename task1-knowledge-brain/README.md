# Task 1: Knowledge Brain – RAG-Powered Product Knowledge System

The **Knowledge Brain** is an autonomous retrieval-augmented generation (RAG) backend engineered for technical support on the Brilliant Directories platform. It crawls documentation via sitemaps, extracts structured content and contextual screenshots, segments articles with section-aware semantic chunking, indexes embeddings in ChromaDB, and provides an API for answering user inquiries with citations and confidence-scored human escalation.

---

## Architecture Overview

```
Sitemap XML ──► Web Crawler ──► HTML Parser ──► Semantic Chunker ──► ChromaDB Vector Store
(Brilliant       (Rate-limited   (Breadcrumbs,   (Section-aware       (Cosine distance
 Directories)    Async HTTP)     Headings, IMG)   Token Overlap)      Embeddings)
                                                                           │
                                                                           ▼
User / Agent ──► FastAPI (/query) ──► RAG Engine ──► Claude Sonnet 4 ──► Answer + Sources
                 └─ /escalations ◄──── (Low Conf) ◄── Claude Haiku 4     + Screenshots
```

---

## Core Components

### 1. Ingestion Pipeline (`ingestion/`)
- **`crawler.py`**:
  - `SitemapParser`: Extracts and filters URLs targeting `/support/solutions/` articles and folders.
  - `WebCrawler`: Asynchronous politely rate-limited crawler (`asyncio.Semaphore`, configurable delay) with MD5 content hashing and change detection.
- **`parser.py`**:
  - `ArticleParser`: Cleans navigation/boilerplate, extracts titles, category/folder hierarchy from breadcrumbs, structured markdown, and image tags with adjacent contextual text.
- **`chunker.py`**:
  - `ArticleChunker`: Splits content into semantically coherent sections with `cl100k_base` token-counted overlaps and associates screenshots to chunks based on text proximity.
- **`pipeline.py`**:
  - `IngestionPipeline`: Orchestrates end-to-end flow with run state tracking, detection of removed articles, and vector store synchronization.

### 2. Knowledge Service & REST API (`app/`)
- **`vector_store.py`**: Persistent ChromaDB store (`knowledge_brain_articles` collection) with rich metadata indexing and cosine similarity search.
- **`database.py`**: Async SQLite persistence for tracking page crawl history, image metadata, human escalations, and prompt versioning.
- **`rag_engine.py`**:
  - Evaluates confidence using Claude Haiku.
  - Synthesizes answers using Claude Sonnet with strict context-adherence rules.
  - Automatically creates an escalation record when retrieved evidence is insufficient.
- **`main.py`**: FastAPI application exposing endpoints:
  - `POST /query`: Semantic retrieval and Claude-generated answer with citations and screenshot links.
  - `POST /ingest`: Trigger background ingestion run (full or incremental).
  - `GET /ingest/status`: Current pipeline status and article counts.
  - `GET /escalations`: List pending human escalation tickets.
  - `POST /escalations/{id}/resolve`: Resolve escalation with expert knowledge and auto-index into knowledge base.
  - `GET /health` & `GET /stats`: System uptime, article counts, chunk statistics, and database status.

---

## Configuration

Set up environment variables in `.env` (derived from `.env.example`):

```bash
# Required for Claude generation
ANTHROPIC_API_KEY=your-anthropic-key

# Service Settings
KNOWLEDGE_BRAIN_HOST=0.0.0.0
KNOWLEDGE_BRAIN_PORT=8000
SITEMAP_URL=https://support.brilliantdirectories.com/support/sitemap.xml
CRAWL_DELAY_SECONDS=2
CRAWL_CONCURRENCY=3
CHROMA_PERSIST_DIR=./chroma_db
DATABASE_URL=sqlite:///./data/knowledge_brain.db
```

---

## Running the Service

```bash
# Run FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

---

## Running Automated Tests

```bash
pytest tests/ -v
```
