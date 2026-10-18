"""
Unit tests for ScopeGenerator
"""
import pytest
from app.scope_generator import ScopeGenerator
from app.models import (
    DiscoveryAnalysis, RequirementItem, RequirementCategory,
    PriorityLevel, ComplexityLevel,
)


def test_scope_generator_creates_phases_and_pricing():
    generator = ScopeGenerator(hourly_rate=150.0)

    analysis = DiscoveryAnalysis(
        meeting_id="MEET-TEST-SOW",
        project_title="Artisan Guild Scoping",
        client_name="Elena Chen",
        client_company="ArtisanGuild",
        executive_summary="Directory for handmade craftspeople.",
        business_model="Monthly membership fee",
        target_audience="Artisans and art collectors",
        timeline_requested="5 weeks",
        requirements=[
            RequirementItem(
                id="REQ-01",
                title="Stripe Subscription Setup",
                description="Configure recurring plans.",
                category=RequirementCategory.CORE_SETUP,
                estimated_hours=8.0,
            ),
            RequirementItem(
                id="REQ-02",
                title="Member CSV Ingestion",
                description="Import 3,500 artisan records.",
                category=RequirementCategory.DATA_MIGRATION,
                estimated_hours=12.0,
            ),
        ],
        out_of_scope=["Native iOS app"],
        technical_risks=[],
        recommended_addons=[{"name": "Photo Albums", "justification": "Portfolio showcase"}],
    )

    sow = generator.generate_sow(analysis, custom_rate=150.0)

    assert sow.sow_id.startswith("SOW-TEST-SOW")
    assert sow.hourly_rate == 150.0
    assert len(sow.phases) == 4
    assert sow.total_hours > 0
    assert sow.total_cost == sow.total_hours * 150.0

    # Verify milestones
    assert len(sow.milestones) == 3
    pct_sum = sum(m.payment_percentage for m in sow.milestones)
    assert pct_sum == 100

    # Verify Markdown output
    assert "# Scope of Work (SOW): Artisan Guild Scoping" in sow.markdown_document
    assert "$150.00/hour" in sow.markdown_document
