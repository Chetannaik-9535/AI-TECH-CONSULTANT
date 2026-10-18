# Task 3: Meeting to Scope – AI Discovery Call Analysis & SOW Generator

**Meeting to Scope** is an AI-powered solutions architecture and scoping engine designed for technical consultants working in the Brilliant Directories platform ecosystem. It ingests client discovery call transcripts (Zoom, Google Meet, Teams), extracts functional and technical requirements, maps platform-native add-ons to prevent bespoke over-engineering, identifies technical risks and boundaries, and outputs an executive-ready, phased Scope of Work (SOW) document with effort hours and milestone fee schedules.

---

## Architecture Overview

```
Meeting Transcript ──► MeetingExtractor ──► DiscoveryAnalysis
(Zoom/Teams audio/vtt)  (Claude Sonnet/Haiku) (Requirements, Risks, Out-of-Scope)
                                                       │
                                                       ▼
                                                ScopeGenerator
                                                (Phases 1-4, Deliverables,
                                                 Hours & Cost @ $150/hr)
                                                       │
                                                       ▼
                      FastAPI (Port 8001) ──► Interactive Web Dashboard
                      (/api/meetings)          (Timeline, Live SOW Editor,
                      (/api/generate-sow)       Markdown Export)
```

---

## Core Capabilities

1. **Discovery Transcript Parsing**:
   - Ingests raw meeting transcripts with speaker turns and timestamp cues.
   - Diarization parsing highlighting consultant technical advice vs. client requests.

2. **AI Requirement Extraction**:
   - Analyzes business models (e.g. claimable listings, lead purchase credits, multi-practitioner sub-accounts).
   - Categorizes requirements across: *Core Setup*, *Functional Features*, *Data Migration*, *Third-Party Webhooks (Twilio/SendGrid/Zapier)*, and *Custom PHP/Widgets*.
   - Specifies native Brilliant Directories add-ons (*Claim Listings Add-on*, *Lead Routing*, *Sub-Accounts Add-on*, *Reviews Add-on*) to minimize bespoke development.
   - Formulates explicit Phase 1 Out-of-Scope boundaries to eliminate scope creep.

3. **Scope of Work (SOW) Generation**:
   - Structures delivery into 4 sequential phases:
     - **Phase 1**: Environment Provisioning, Brand Design & Architecture
     - **Phase 2**: Custom Functionality, Membership Monetization & Workflows
     - **Phase 3**: Data Migration, Third-Party Webhooks & Automation
     - **Phase 4**: Quality Assurance, Security Audit, Training & Launch
   - Dynamic hours and cost calculation based on configurable hourly consulting rates (default $150/hr).
   - Structured 3-stage milestone payment schedule (40% initiation, 30% midway, 30% acceptance).
   - One-click copy and download as GitHub-compliant Markdown document.

4. **Interactive Dashboard (Port 8001)**:
   - Built-in discovery session library (*MedMatch Pro Healthcare*, *HomeService Hub Contractors*, *ArtisanGuild Craftspeople*).
   - Side-by-side transcript reader and discovery requirements viewer.
   - Live editable Scope of Work preview with phase expansion and instant rate recalculation.

---

## API Endpoints

- `GET /health`: Service health check.
- `GET /api/meetings`: List all discovery meetings.
- `GET /api/meetings/{id}`: Retrieve meeting metadata and full transcript.
- `POST /api/meetings`: Ingest new meeting transcript.
- `POST /api/meetings/{id}/analyze`: Run AI requirement extraction.
- `POST /api/meetings/{id}/generate-sow?hourly_rate=150`: Compile phased SOW and pricing.
- `GET /api/sow/{sow_id}`: Retrieve SOW JSON.
- `GET /api/sow/{sow_id}/markdown`: Download clean Markdown document.

---

## Running the Application

```bash
cd task3-meeting-to-scope
pip install -e .
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Open dashboard in browser:
`http://localhost:8001`
Open OpenAPI documentation:
`http://localhost:8001/docs`

---

## Running Automated Tests

```bash
pytest tests/ -v
```
