"""
Unit tests for MeetingExtractor
"""
import pytest
from app.extractor import MeetingExtractor
from app.models import MeetingInput, MeetingMetadata


@pytest.mark.asyncio
async def test_extractor_rule_based_analysis():
    extractor = MeetingExtractor()

    transcript = """
    [00:00] Consultant: Let's discuss your requirements.
    [00:30] Client: We need to import 10,000 contractors via CSV with geocoded coordinates.
    [01:00] Client: We also want a claim listing workflow where contractors pay via Stripe.
    [01:30] Client: When leads arrive, send an instant SMS alert via Twilio webhook.
    [02:00] Client: We do not want mobile apps or telemedicine video calls right now.
    """

    meta = MeetingMetadata(
        id="MEET-TEST-EXTRACT",
        title="Contractor Network Discovery",
        client_name="Marcus Thorne",
        client_company="Thorne Ventures",
        date="2026-03-15",
        duration_minutes=40,
        participants=["Marcus Thorne", "Consultant"],
    )

    meeting_input = MeetingInput(
        metadata=meta,
        transcript=transcript,
        custom_notes="Focus on pay-per-lead and Twilio webhooks.",
    )

    analysis = await extractor.analyze_meeting(meeting_input)

    assert analysis is not None
    assert analysis.meeting_id == "MEET-TEST-EXTRACT"
    assert len(analysis.requirements) >= 3

    req_titles = [r.title.lower() for r in analysis.requirements]
    assert any("import" in t or "csv" in t for t in req_titles)
    assert any("claim" in t for t in req_titles)
    assert any("sms" in t or "twilio" in t or "webhook" in t for t in req_titles)

    # Check out of scope
    assert len(analysis.out_of_scope) > 0

    # Check technical risks
    assert len(analysis.technical_risks) > 0
