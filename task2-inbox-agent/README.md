# Task 2: Inbox Agent – Autonomous Ticket Triage & Resolution System

The **Inbox Agent** is an AI-powered customer inquiry management platform designed for technical consultants on the Brilliant Directories platform. It automates inbound ticket ingestion, intent classification, sentiment analysis, urgency prioritization, and grounds resolution drafts in verified Brilliant Directories help-center documentation sourced via the Task 1 Knowledge Brain.

---

## Key Features

1. **Autonomous Ticket Triage**:
   - Classifies inquiries across categories: *Domains & SSL*, *Finance & Billing*, *Member Management*, *Custom Code & Widgets*, *Email & Notifications*, *SEO & Content*.
   - Calculates dynamic Urgency Scores (0–100) taking into account customer SLA tiers (*VIP Enterprise*, *Directory Pro*, *Starter*) and sentiment.
   - Detects customer sentiment (*Frustrated*, *Angry*, *Concerned*, *Inquisitive*, *Neutral*).

2. **Knowledge-Grounded Resolution Drafting**:
   - Queries Task 1 Knowledge Brain (`/query`) for verified documentation snippets and step-by-step instructions.
   - Provides citations with links to official Brilliant Directories help articles.
   - Allows consultants to regenerate drafts in multiple tones (*Professional*, *Empathetic*, *Technical*, *Step-by-Step*).

3. **Human Escalation Workflow**:
   - Directly escalates ambiguous, mission-critical, or custom code issues to Senior Platform Engineering.
   - Syncs escalation tickets with the Task 1 Knowledge Brain `/escalations` database.

4. **Live Interactive Dashboard (Port 3000)**:
   - Modern glassmorphic dark-mode UI with live metric counters (*Needs Review*, *Auto-Drafted*, *Escalated*, *Resolved*).
   - Inbound simulation modal preloaded with realistic Brilliant Directories support scenarios.
   - Analytics modal displaying deflection rate (78%), resolution speed (1.4s), and category breakdowns.

---

## Architecture

```
Inbound Email / Ticket ──► Inbox Agent (Port 3000)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       Automated AI Triage             Knowledge Brain Query
       (Category, Sentiment, Urgency)  (http://localhost:8000/query)
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     Grounded Resolution Draft
                     (Citations + Step-by-Step)
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
         Approve & Send                Escalate to Human
         (Mark Resolved)               (Forward to KB /escalations)
```

---

## Running the Service

```bash
cd task2-inbox-agent
npm install
npm start
```

Access the interactive dashboard in your browser at:
`http://localhost:3000`
