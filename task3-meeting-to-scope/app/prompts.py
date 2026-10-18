"""
AI Tech Consultant - Meeting to Scope
Prompt templates for Claude-powered transcript analysis and SOW generation.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an elite AI Technical Solutions Consultant specializing in the Brilliant Directories platform ecosystem.
Your role:
- Analyze client discovery meeting transcripts with extreme technical precision.
- Identify core business objectives, monetization mechanics, and platform requirements.
- Distinguish between standard platform configurations and tasks requiring custom PHP widgets, API webhooks, or third-party integrations.
- Always recommend native Brilliant Directories add-ons (e.g., Claim Listings, Sub-Accounts, Lead Routing, Digital Products) when they can fulfill requirements out-of-the-box, saving the client custom development costs.
- Flag risks, edge cases, and scope creep boundaries clearly.
"""

EXTRACTION_PROMPT_TEMPLATE = """Analyze the following client discovery call transcript for a Brilliant Directories project.

## Meeting Details
- Title: {title}
- Client: {client_name} ({client_company})
- Date: {date}
- Participants: {participants}
- Consultant Notes: {custom_notes}

## Transcript
{transcript}

## Instructions
Extract and return a comprehensive structured JSON object with the following fields:
1. "executive_summary": 2-3 sentence overview of the project vision and goals.
2. "business_model": How the directory will generate revenue (membership fees, claim fees, lead purchases, etc.).
3. "target_audience": Primary users (both directory listers and public searchers).
4. "timeline_requested": Target launch timeline mentioned by the client.
5. "requirements": A list of requirement objects, each with:
   - "id": string like "REQ-01", "REQ-02"
   - "title": brief requirement title
   - "description": specific functional or technical explanation
   - "category": one of ["Core Setup & Configuration", "Functional Features", "Third-Party Integrations", "Custom PHP / Widgets", "Data Migration & Import", "Design & Branding", "Email & Notifications"]
   - "priority": one of ["Must Have", "Should Have", "Nice to Have"]
   - "complexity": one of ["Low", "Medium", "High"]
   - "estimated_hours": realistic number of consulting hours (e.g. 4, 8, 12)
   - "recommended_bd_addon": optional native BD add-on name if applicable
6. "out_of_scope": list of clear exclusions mentioned to prevent scope creep.
7. "technical_risks": list of objects with "risk", "impact", "mitigation".
8. "recommended_addons": list of native Brilliant Directories add-ons with name and justification.

Return valid JSON only.
"""

SOW_GENERATION_PROMPT = """Using the structured discovery requirements below, generate an executive-ready, professional Scope of Work (SOW) markdown document for {client_name} of {client_company}.

## Project Information
- Project Title: {project_title}
- Platform: Brilliant Directories
- Consultant Rate: ${hourly_rate}/hour

## Discovery Analysis & Requirements
{discovery_json}

## Instructions for SOW Document
Write a comprehensive, publication-quality Scope of Work document formatted in clean GitHub Markdown:
1. **Document Header**: Project Title, Client Name, Company, Date, Consultant.
2. **Executive Overview**: Problem statement, business model, and project goals.
3. **Phased Deliverables**:
   - Organize deliverables into 3-4 logical sequential phases (e.g., Phase 1: Core Architecture & Setup, Phase 2: Feature Development & Integrations, Phase 3: Data Migration & Testing, Phase 4: Launch & Knowledge Transfer).
   - For each phase, list specific deliverables, bulleted technical tasks, estimated hours, and phase subtotal.
4. **Platform Optimization & Native Add-ons**:
   - Detail the recommended Brilliant Directories add-ons and explain cost savings over custom code.
5. **Timeline & Milestone Payment Schedule**:
   - Table showing Milestone Name, Target Week, Deliverables, and Payment % (e.g. 40% deposit, 30% midway, 30% pre-launch).
6. **Project Assumptions & Client Responsibilities**:
   - Specific items required from the client (content, logo, API keys, domain DNS access).
7. **Change Order & Sign-off Terms**:
   - Standard consulting procedures for scope modifications.

Maintain an authoritative, transparent, and collaborative consulting tone.
"""
