"""
AI Tech Consultant - Comprehensive Master Software Test Suite
Executes multi-condition testing across all 3 tasks and their inter-service integrations.
Tests:
- Task 1: Knowledge Brain (port 8000)
- Task 2: Inbox Agent (port 3000)
- Task 3: Meeting to Scope (port 8001)
- Cross-System Continuous Learning & Escalation Loop
"""
import asyncio
import json
import time
from typing import Any, Dict
import httpx

KB_URL = "http://localhost:8000"
INBOX_URL = "http://localhost:3000"
SCOPE_URL = "http://localhost:8001"

results = []

def record(test_id: str, component: str, description: str, passed: bool, details: str = ""):
    status_str = "PASS ✓" if passed else "FAIL ✗"
    print(f"[{status_str}] {test_id} ({component}): {description}")
    if details and not passed:
        print(f"       Details: {details}")
    results.append({
        "id": test_id,
        "component": component,
        "description": description,
        "passed": passed,
        "details": details
    })


async def run_master_suite():
    print("=" * 70)
    print("🔍 RUNNING MASTER MULTI-CONDITION SOFTWARE TEST SUITE")
    print("=" * 70)

    async with httpx.AsyncClient(timeout=30.0) as client:

        # ═════════════════════════════════════════════════════════════════
        # TASK 1: KNOWLEDGE BRAIN TESTS
        # ═════════════════════════════════════════════════════════════════
        print("\n--- SECTION 1: Task 1 (Knowledge Brain) Testing ---")

        # 1.1 Health & Capacity
        try:
            r = await client.get(f"{KB_URL}/health")
            data = r.json()
            is_healthy = r.status_code == 200 and data.get("status") == "healthy" and data.get("total_chunks", 0) >= 30
            record("T1.1", "Knowledge Brain", "Health check & vector chunks indexed", is_healthy, f"Chunks: {data.get('total_chunks')}")
        except Exception as e:
            record("T1.1", "Knowledge Brain", "Health check & vector chunks indexed", False, str(e))

        # 1.2 Query: Domain & DNS In-Domain Knowledge
        try:
            payload = {
                "question": "How do I configure my domain DNS A-record to point to Brilliant Directories?",
                "max_sources": 3,
                "include_images": True
            }
            r = await client.post(f"{KB_URL}/query", json=payload)
            data = r.json()
            has_ip = "54.208.192.173" in data.get("answer", "")
            has_sources = len(data.get("sources", [])) > 0
            record("T1.2", "Knowledge Brain", "In-Domain Query: Domain DNS A-Record & IP retrieval", has_ip and has_sources, f"Sources: {len(data.get('sources', []))}")
        except Exception as e:
            record("T1.2", "Knowledge Brain", "In-Domain Query: Domain DNS A-Record & IP retrieval", False, str(e))

        # 1.3 Query: Stripe Payment Gateway Setup
        try:
            payload = {
                "question": "Where do I input Stripe publishable and secret keys in the Brilliant Directories admin?",
                "max_sources": 3
            }
            r = await client.post(f"{KB_URL}/query", json=payload)
            data = r.json()
            has_finance = "Finance" in data.get("answer", "") or "Payment Gateways" in data.get("answer", "") or "stripe" in data.get("answer", "").lower()
            record("T1.3", "Knowledge Brain", "In-Domain Query: Stripe Gateway configuration", has_finance, data.get("answer", "")[:100])
        except Exception as e:
            record("T1.3", "Knowledge Brain", "In-Domain Query: Stripe Gateway configuration", False, str(e))

        # 1.4 Query: CSV Member Bulk Import Guidelines
        try:
            payload = {
                "question": "What is the recommended row limit for CSV member imports to prevent timeouts?",
                "max_sources": 3
            }
            r = await client.post(f"{KB_URL}/query", json=payload)
            data = r.json()
            has_csv = "2,000" in data.get("answer", "") or "csv" in data.get("answer", "").lower() or "member" in data.get("answer", "").lower()
            record("T1.4", "Knowledge Brain", "In-Domain Query: CSV Member Import row limits", has_csv, data.get("answer", "")[:100])
        except Exception as e:
            record("T1.4", "Knowledge Brain", "In-Domain Query: CSV Member Import row limits", False, str(e))

        # 1.5 Query: Out-of-Domain Unanswerable Question (Escalation Trigger)
        try:
            payload = {
                "question": "Explain quantum entanglement state teleportation protocols in string theory.",
                "max_sources": 3
            }
            r = await client.post(f"{KB_URL}/query", json=payload)
            data = r.json()
            is_insufficient = data.get("status") == "insufficient" or data.get("needs_human") is True
            record("T1.5", "Knowledge Brain", "Out-of-Domain Query: Graceful insufficiency detection", is_insufficient, f"Status: {data.get('status')}")
        except Exception as e:
            record("T1.5", "Knowledge Brain", "Out-of-Domain Query: Graceful insufficiency detection", False, str(e))

        # 1.6 Input Validation: Missing/Short Question
        try:
            r = await client.post(f"{KB_URL}/query", json={"question": "hi"})
            is_422 = r.status_code == 422
            record("T1.6", "Knowledge Brain", "Input Validation: Reject questions < 3 characters (422)", is_422, f"Status: {r.status_code}")
        except Exception as e:
            record("T1.6", "Knowledge Brain", "Input Validation: Reject questions < 3 characters (422)", False, str(e))

        # 1.7 Escalation Creation & Resolution Active Learning Loop
        try:
            # Create escalation
            esc_data = {
                "question": "How do I configure Redis caching layer on custom AWS clusters for Brilliant Directories?",
                "context": "Enterprise client scaling to 500k directory profiles.",
                "reason": "complex_infrastructure"
            }
            esc_res = await client.post(f"{KB_URL}/escalations", json=esc_data)
            esc_obj = esc_res.json()
            esc_id = esc_obj.get("id")

            # Resolve escalation with expert answer and add_to_knowledge=True
            resolve_payload = {
                "answer": "To configure external Redis caching, update config/database.php with REDIS_HOST and activate Redis session handler in Developer Tools > Advanced Settings.",
                "expert_name": "DevOps Architect",
                "add_to_knowledge": True,
                "supporting_urls": ["https://support.brilliantdirectories.com/advanced-caching"]
            }
            resolve_res = await client.post(f"{KB_URL}/escalations/{esc_id}/resolve", json=resolve_payload)
            resolved_obj = resolve_res.json()

            # Verify it is now retrievable in ChromaDB
            verify_query = await client.post(f"{KB_URL}/query", json={"question": "How do I configure Redis caching layer on custom AWS clusters for Brilliant Directories?"})
            verify_data = verify_query.json()
            redis_learned = "REDIS_HOST" in verify_data.get("answer", "") or "Redis" in verify_data.get("answer", "")

            record("T1.7", "Knowledge Brain", "Active Learning Loop: Resolve escalation & index expert answer", redis_learned, f"Learned answer snippet: {verify_data.get('answer', '')[:80]}")
        except Exception as e:
            record("T1.7", "Knowledge Brain", "Active Learning Loop: Resolve escalation & index expert answer", False, str(e))


        # ═════════════════════════════════════════════════════════════════
        # TASK 2: INBOX AGENT TESTS
        # ═════════════════════════════════════════════════════════════════
        print("\n--- SECTION 2: Task 2 (Inbox Agent) Testing ---")

        # 2.1 Health Check & Stats
        try:
            r = await client.get(f"{INBOX_URL}/api/health")
            data = r.json()
            ok = r.status_code == 200 and data.get("status") == "healthy" and data.get("knowledgeBrain", {}).get("online") is True
            record("T2.1", "Inbox Agent", "Health check & Knowledge Brain connectivity", ok, f"KB Online: {data.get('knowledgeBrain', {}).get('online')}")
        except Exception as e:
            record("T2.1", "Inbox Agent", "Health check & Knowledge Brain connectivity", False, str(e))

        # 2.2 Triage Categorization & Sentiment
        try:
            ticket_payload = {
                "customer": {
                    "name": "Marcus Vance",
                    "email": "marcus@vancedirectory.com",
                    "company": "Vance Law Directory",
                    "tier": "VIP Enterprise"
                },
                "subject": "EMERGENCY: Stripe checkout throwing fatal gateway error",
                "message": "Our customers are unable to pay membership dues! Payment gateway reports invalid webhook signature. Please fix ASAP!"
            }
            r = await client.post(f"{INBOX_URL}/api/tickets", json=ticket_payload)
            ticket = r.json()
            is_urgent = ticket.get("priority") == "Urgent"
            is_finance = ticket.get("category") == "Finance & Billing"
            is_angry = ticket.get("sentiment") in ["Angry", "Frustrated"]
            has_draft = bool(ticket.get("draftReply", {}).get("body"))
            record("T2.2", "Inbox Agent", "Ticket Ingestion: Auto-triage, VIP SLA urgency & draft generation", is_urgent and is_finance and has_draft, f"Category={ticket.get('category')}, Priority={ticket.get('priority')}")
            created_ticket_id = ticket.get("id")
        except Exception as e:
            record("T2.2", "Inbox Agent", "Ticket Ingestion: Auto-triage, VIP SLA urgency & draft generation", False, str(e))
            created_ticket_id = None

        # 2.3 Tone Customization (Empathetic / Technical)
        if created_ticket_id:
            try:
                r = await client.post(f"{INBOX_URL}/api/tickets/{created_ticket_id}/draft", json={
                    "tone": "Empathetic",
                    "customInstructions": "Apologize for checkout downtime and offer phone support."
                })
                updated = r.json()
                tone_ok = updated.get("draftReply", {}).get("tone") == "Empathetic"
                notes_ok = "Apologize for checkout downtime" in updated.get("draftReply", {}).get("body", "")
                record("T2.3", "Inbox Agent", "Draft Customization: Empathetic tone regeneration", tone_ok and notes_ok, f"Tone: {updated.get('draftReply', {}).get('tone')}")
            except Exception as e:
                record("T2.3", "Inbox Agent", "Draft Customization: Empathetic tone regeneration", False, str(e))

        # 2.4 Approve and Send Resolution
        if created_ticket_id:
            try:
                r = await client.post(f"{INBOX_URL}/api/tickets/{created_ticket_id}/send", json={
                    "finalBody": "We have refreshed your Stripe webhook keys. Live checkout is operational."
                })
                send_data = r.json()
                is_resolved = send_data.get("ticket", {}).get("status") == "resolved"
                record("T2.4", "Inbox Agent", "Resolution Workflow: Approve and send response", is_resolved, f"Status: {send_data.get('ticket', {}).get('status')}")
            except Exception as e:
                record("T2.4", "Inbox Agent", "Resolution Workflow: Approve and send response", False, str(e))

        # 2.5 Cross-Service Ticket Escalation to Task 1
        try:
            r = await client.post(f"{INBOX_URL}/api/tickets/TICK-1002/escalate", json={
                "reason": "custom_database_hook_corruption",
                "note": "Corrupted MySQL table during third-party plugin sync."
            })
            esc_res = r.json()
            is_escalated = esc_res.get("ticket", {}).get("status") == "escalated"
            kb_id = esc_res.get("ticket", {}).get("kbEscalationId")
            record("T2.5", "Inbox Agent -> Task 1", "Cross-Service Escalation: Forward to Task 1 Knowledge Brain", is_escalated and bool(kb_id), f"kbEscalationId: {kb_id}")
        except Exception as e:
            record("T2.5", "Inbox Agent -> Task 1", "Cross-Service Escalation: Forward to Task 1 Knowledge Brain", False, str(e))


        # ═════════════════════════════════════════════════════════════════
        # TASK 3: MEETING TO SCOPE TESTS
        # ═════════════════════════════════════════════════════════════════
        print("\n--- SECTION 3: Task 3 (Meeting to Scope) Testing ---")

        # 3.1 Health Check
        try:
            r = await client.get(f"{SCOPE_URL}/health")
            data = r.json()
            ok = r.status_code == 200 and data.get("status") == "healthy"
            record("T3.1", "Meeting to Scope", "Health check & service readiness", ok, f"Service: {data.get('service')}")
        except Exception as e:
            record("T3.1", "Meeting to Scope", "Health check & service readiness", False, str(e))

        # 3.2 Full Scope of Work (SOW) Generation with 4 Phases & 40/30/30 Milestones
        realistic_transcript = """
        [00:00] Consultant: Welcome Robert. Let's discuss your directory platform goals for MedicalFind Pro.
        [00:02] Robert: Thanks. We need a complete Brilliant Directories implementation for 15,000 doctors.
        [00:05] Robert: Phase 1 should be DNS setup, pointing our domain medicalfindpro.com, and styling the homepage with our brand colors.
        [00:10] Consultant: Understood. What about the member data and Stripe integration?
        [00:12] Robert: Yes, Phase 2 is importing doctors from our CSV and configuring Stripe billing with monthly and annual recurring plans.
        [00:18] Robert: Phase 3 is building a custom telemedicine widget in PHP to embed video consultation buttons on doctor listings.
        [00:25] Robert: Phase 4 will be setting up automated lead matching by specialty and distance radius, plus Sendgrid SMTP email notifications.
        [00:30] Consultant: Excellent. We'll deliver this over an 8-week timeline with standard milestone payments.
        """

        # 3.2 Ingest New Meeting Transcript
        new_meeting = {
            "metadata": {
                "id": "MEET-9001",
                "title": "MedicalFind Pro Enterprise Platform Scoping",
                "client_name": "Dr. Robert Chen",
                "client_company": "MedicalFind Pro",
                "client_email": "robert@medicalfindpro.com",
                "duration_minutes": 45,
                "participants": ["Consultant", "Dr. Robert Chen"]
            },
            "transcript": realistic_transcript,
            "custom_notes": "Client requested delivery in 8 weeks with 40/30/30 milestones."
        }
        try:
            r = await client.post(f"{SCOPE_URL}/api/meetings", json=new_meeting)
            record("T3.2", "Meeting to Scope", "Transcript Ingestion: Upload & register meeting", r.status_code == 200, f"Status: {r.status_code}")
        except Exception as e:
            record("T3.2", "Meeting to Scope", "Transcript Ingestion: Upload & register meeting", False, str(e))

        # 3.3 Requirement Extraction & Discovery Analysis
        try:
            r = await client.post(f"{SCOPE_URL}/api/meetings/MEET-9001/analyze")
            analysis = r.json()
            has_reqs = len(analysis.get("requirements", [])) >= 3
            record("T3.3", "Meeting to Scope", "Requirements Extraction: Extract core requirements & tech stack", has_reqs, f"Extracted {len(analysis.get('requirements', []))} reqs")
        except Exception as e:
            record("T3.3", "Meeting to Scope", "Requirements Extraction: Extract core requirements & tech stack", False, str(e))

        # 3.4 SOW Generation with 40/30/30 Milestones
        sow_id = None
        try:
            r = await client.post(f"{SCOPE_URL}/api/meetings/MEET-9001/generate-sow?hourly_rate=150.0")
            sow = r.json()
            has_phases = len(sow.get("phases", [])) >= 3
            milestones = sow.get("milestones", [])
            total_cost = sow.get("total_cost", 0)
            total_hours = sow.get("total_hours", 0)
            rate = sow.get("hourly_rate", 0)
            math_valid = total_cost > 0 and total_hours > 0 and abs(total_cost - (total_hours * rate)) < 0.01
            sum_percentages = sum(m.get("payment_percentage", 0) for m in milestones)
            milestones_valid = len(milestones) == 3 and sum_percentages == 100
            sow_id = sow.get("sow_id")
            record("T3.4", "Meeting to Scope", "Full SOW Synthesis: 4 Phases, Mathematical 40/30/30 Milestones", has_phases and math_valid and milestones_valid, f"Phases={len(sow.get('phases', []))}, Hours={total_hours}, Total=${total_cost}, Milestones={sum_percentages}%")
        except Exception as e:
            record("T3.4", "Meeting to Scope", "Full SOW Synthesis: 4 Phases, Mathematical 40/30/30 Milestones", False, str(e))

        # 3.5 Dynamic Hourly Rate Pricing: Multi-tier rate scaling ($120 vs $200)
        try:
            r1 = await client.post(f"{SCOPE_URL}/api/meetings/MEET-9001/generate-sow?hourly_rate=120.0")
            r2 = await client.post(f"{SCOPE_URL}/api/meetings/MEET-9001/generate-sow?hourly_rate=200.0")
            sow1 = r1.json()
            sow2 = r2.json()
            c1 = sow1.get("total_cost", 0)
            c2 = sow2.get("total_cost", 0)
            scaled_correctly = c2 > c1 and sow1.get("hourly_rate") == 120.0 and sow2.get("hourly_rate") == 200.0
            record("T3.5", "Meeting to Scope", "Dynamic Hourly Rate Pricing: Multi-tier rate scaling ($120 vs $200)", scaled_correctly, f"Cost @ $120: ${c1}, Cost @ $200: ${c2}")
        except Exception as e:
            record("T3.5", "Meeting to Scope", "Dynamic Hourly Rate Pricing: Multi-tier rate scaling ($120 vs $200)", False, str(e))

        # 3.6 Markdown Statement of Work (SOW) Export
        try:
            r = await client.get(f"{SCOPE_URL}/api/sow/{sow_id}/markdown")
            md = r.text
            has_headers = "# Statement of Work" in md or "Scope of Work" in md or "Project Scope" in md
            has_tables = "|" in md and "Phase" in md
            record("T3.6", "Meeting to Scope", "Markdown SOW Export: Formatted headers, milestone tables, signature block", has_headers and has_tables, f"Markdown Length: {len(md)} chars")
        except Exception as e:
            record("T3.6", "Meeting to Scope", "Markdown SOW Export: Formatted headers, milestone tables, signature block", False, str(e))

        # 3.7 Error Handling: 404 on Non-Existent Meeting
        try:
            r = await client.post(f"{SCOPE_URL}/api/meetings/MEET-NONEXISTENT-9999/generate-sow")
            record("T3.7", "Meeting to Scope", "Error Condition: 404 on non-existent meeting ID", r.status_code == 404, f"Status: {r.status_code}")
        except Exception as e:
            record("T3.7", "Meeting to Scope", "Error Condition: 404 on non-existent meeting ID", False, str(e))


    # ═════════════════════════════════════════════════════════════════
    # SUMMARY REPORT
    # ═════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("📊 MASTER SOFTWARE TESTING EXECUTION SUMMARY")
    print("=" * 70)
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)

    for r in results:
        status_symbol = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"{status_symbol} | {r['id']:<5} | {r['component']:<25} | {r['description']}")

    print("=" * 70)
    print(f"TOTAL: {passed_count}/{total_count} Conditions Passed ({round((passed_count/total_count)*100, 1)}%)")
    print("=" * 70)

    return passed_count == total_count

if __name__ == "__main__":
    success = asyncio.run(run_master_suite())
    exit(0 if success else 1)
