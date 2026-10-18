"""
Unit tests for Meeting to Scope Pydantic Models
"""
import pytest
from app.models import (
    MeetingMetadata, MeetingInput, RequirementItem, RiskItem,
    DiscoveryAnalysis, ScopeOfWork, RequirementCategory, PriorityLevel,
)


def test_meeting_metadata_validation():
    meta = MeetingMetadata(
        id="MEET-TEST-1",
        title="Test Discovery Session",
        client_name="Sarah Connor",
        client_company="Cyberdyne Media",
        date="2026-03-20",
        duration_minutes=45,
        participants=["Sarah Connor", "Consultant"],
    )
    assert meta.id == "MEET-TEST-1"
    assert meta.duration_minutes == 45
    assert len(meta.participants) == 2


def test_requirement_item_defaults():
    req = RequirementItem(
        id="REQ-01",
        title="Custom Geocoding Search",
        description="Filter doctors within 25 miles of postal code.",
        category=RequirementCategory.FUNCTIONAL,
    )
    assert req.priority == PriorityLevel.MUST_HAVE
    assert req.estimated_hours == 6.0


def test_discovery_analysis_structure():
    analysis = DiscoveryAnalysis(
        meeting_id="MEET-TEST-1",
        project_title="Doctor Directory Scoping",
        client_name="Dr. Smith",
        client_company="ClinicGroup",
        executive_summary="Directory for regional practitioners.",
        business_model="Annual subscription plans",
        target_audience="Patients seeking certified specialists",
        timeline_requested="6 weeks",
        requirements=[
            RequirementItem(
                id="REQ-01",
                title="Stripe Setup",
                description="Setup payment gateways.",
                category=RequirementCategory.CORE_SETUP,
                estimated_hours=8.0,
            )
        ],
        out_of_scope=["Telemedicine video calling"],
        technical_risks=[
            RiskItem(
                risk="Bulk import rate limit",
                impact="Long ingestion time",
                mitigation="Batch processing in chunks of 2,000",
            )
        ],
    )
    assert analysis.meeting_id == "MEET-TEST-1"
    assert len(analysis.requirements) == 1
    assert len(analysis.out_of_scope) == 1
