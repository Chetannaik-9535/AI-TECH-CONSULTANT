"""
AI Tech Consultant - Meeting to Scope
Transcript parsing and AI requirement extraction engine.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

import anthropic

from app.config import get_settings
from app.models import (
    MeetingInput, DiscoveryAnalysis, RequirementItem, RiskItem,
    RequirementCategory, PriorityLevel, ComplexityLevel,
)
from app.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)
settings = get_settings()


class MeetingExtractor:
    """Extracts structured requirements and discovery analysis from meeting transcripts."""

    def __init__(self):
        self._client: Optional[anthropic.Anthropic] = None

    def _get_client(self) -> Optional[anthropic.Anthropic]:
        if not self._client and settings.anthropic_api_key:
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def analyze_meeting(self, meeting_input: MeetingInput) -> DiscoveryAnalysis:
        """Run discovery analysis on meeting transcript."""
        client = self._get_client()

        if client:
            try:
                return await self._analyze_with_claude(client, meeting_input)
            except Exception as e:
                logger.warning(f"Claude API extraction failed, falling back to rule-based engine: {e}")

        # Fallback to intelligent rule-based domain parser
        return self._analyze_with_rules(meeting_input)

    async def _analyze_with_claude(
        self, client: anthropic.Anthropic, meeting_input: MeetingInput
    ) -> DiscoveryAnalysis:
        meta = meeting_input.metadata
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            title=meta.title,
            client_name=meta.client_name,
            client_company=meta.client_company,
            date=meta.date,
            participants=", ".join(meta.participants),
            custom_notes=meeting_input.custom_notes or "None",
            transcript=meeting_input.transcript,
        )

        message = client.messages.create(
            model=settings.claude_fast_model,
            max_tokens=4000,
            system=EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw_text = message.content[0].text.strip()
        # Extract JSON from code fences if present
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()

        data = json.loads(raw_text)

        requirements = []
        for r in data.get("requirements", []):
            try:
                category = RequirementCategory(r.get("category", RequirementCategory.FUNCTIONAL.value))
            except ValueError:
                category = RequirementCategory.FUNCTIONAL

            try:
                priority = PriorityLevel(r.get("priority", PriorityLevel.MUST_HAVE.value))
            except ValueError:
                priority = PriorityLevel.MUST_HAVE

            try:
                complexity = ComplexityLevel(r.get("complexity", ComplexityLevel.MEDIUM.value))
            except ValueError:
                complexity = ComplexityLevel.MEDIUM

            requirements.append(
                RequirementItem(
                    id=r.get("id", f"REQ-{len(requirements)+1:02d}"),
                    title=r.get("title", "Requirement"),
                    description=r.get("description", ""),
                    category=category,
                    priority=priority,
                    complexity=complexity,
                    estimated_hours=float(r.get("estimated_hours", 6.0)),
                    recommended_bd_addon=r.get("recommended_bd_addon"),
                )
            )

        risks = [
            RiskItem(
                risk=rk.get("risk", ""),
                impact=rk.get("impact", ""),
                mitigation=rk.get("mitigation", ""),
            )
            for rk in data.get("technical_risks", [])
        ]

        return DiscoveryAnalysis(
            meeting_id=meta.id,
            project_title=meta.title,
            client_name=meta.client_name,
            client_company=meta.client_company,
            executive_summary=data.get("executive_summary", f"Directory implementation for {meta.client_company}"),
            business_model=data.get("business_model", "Membership subscriptions & directory listings"),
            target_audience=data.get("target_audience", "Industry professionals & searching public"),
            timeline_requested=data.get("timeline_requested", "6-8 weeks"),
            requirements=requirements,
            out_of_scope=data.get("out_of_scope", []),
            technical_risks=risks,
            recommended_addons=data.get("recommended_addons", []),
        )

    def _analyze_with_rules(self, meeting_input: MeetingInput) -> DiscoveryAnalysis:
        """Domain-aware rule-based discovery extractor for Brilliant Directories."""
        meta = meeting_input.metadata
        t_lower = meeting_input.transcript.lower()

        reqs: list[RequirementItem] = []
        req_id = 1

        # Check for core categories & requirements
        if "tier" in t_lower or "membership" in t_lower or "plan" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Tiered Membership Architecture & Stripe Recurring Billing",
                    description="Configure multi-level membership plans with automated recurring subscriptions and custom feature access limits via Stripe.",
                    category=RequirementCategory.CORE_SETUP,
                    priority=PriorityLevel.MUST_HAVE,
                    complexity=ComplexityLevel.LOW,
                    estimated_hours=8.0,
                    recommended_bd_addon="Membership Plan Manager (Native)",
                )
            )
            req_id += 1

        if "claim" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Claim Listings Flow with Admin Approval Moderation",
                    description="Allow prospective members to claim pre-populated directory listings, verify credentials, and trigger automatic plan upgrades upon verification.",
                    category=RequirementCategory.FUNCTIONAL,
                    priority=PriorityLevel.MUST_HAVE,
                    complexity=ComplexityLevel.MEDIUM,
                    estimated_hours=12.0,
                    recommended_bd_addon="Claim Listings Add-on",
                )
            )
            req_id += 1

        if "search" in t_lower or "radius" in t_lower or "zip" in t_lower or "distance" in t_lower or "map" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Geocoded Radius Search & Custom Category Filters",
                    description="Implement Google Maps radial distance search with custom multi-select filtering based on specialized services and locations.",
                    category=RequirementCategory.FUNCTIONAL,
                    priority=PriorityLevel.MUST_HAVE,
                    complexity=ComplexityLevel.MEDIUM,
                    estimated_hours=10.0,
                    recommended_bd_addon="Google Maps Geocoding & Location Search (Native)",
                )
            )
            req_id += 1

        if "lead" in t_lower or "inquiry" in t_lower or "quote" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Automated Lead Distribution & Inquiry Engine",
                    description="Capture client quote and consultation requests, automatically route to matched providers, and manage lead purchase credits.",
                    category=RequirementCategory.FUNCTIONAL,
                    priority=PriorityLevel.MUST_HAVE,
                    complexity=ComplexityLevel.HIGH,
                    estimated_hours=16.0,
                    recommended_bd_addon="Automated Lead Routing Add-on",
                )
            )
            req_id += 1

        if "csv" in t_lower or "import" in t_lower or "migrate" in t_lower or "migration" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Data Cleansing, Geocoding & Batch Member Import",
                    description="Normalize legacy database / CSV files, geocode postal coordinates, and execute segmented batch imports (2,000 records/batch).",
                    category=RequirementCategory.DATA_MIGRATION,
                    priority=PriorityLevel.MUST_HAVE,
                    complexity=ComplexityLevel.MEDIUM,
                    estimated_hours=14.0,
                    recommended_bd_addon="Member Import Tool",
                )
            )
            req_id += 1

        if "sms" in t_lower or "twilio" in t_lower or "webhook" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Real-Time SMS Alert Webhook Integration",
                    description="Configure outbound webhook to Twilio / Zapier to dispatch instant SMS notifications to providers when new inquiries arrive.",
                    category=RequirementCategory.TECHNICAL_INTEGRATIONS,
                    priority=PriorityLevel.SHOULD_HAVE,
                    complexity=ComplexityLevel.MEDIUM,
                    estimated_hours=8.0,
                    recommended_bd_addon="Developer Hub Webhooks",
                )
            )
            req_id += 1

        if "review" in t_lower or "rating" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Star Ratings & Moderated Member Reviews",
                    description="Enable client review submission with multi-criteria ratings and admin moderation queue to prevent spam.",
                    category=RequirementCategory.FUNCTIONAL,
                    priority=PriorityLevel.SHOULD_HAVE,
                    complexity=ComplexityLevel.LOW,
                    estimated_hours=6.0,
                    recommended_bd_addon="Member Reviews Add-on",
                )
            )
            req_id += 1

        if "widget" in t_lower or "php" in t_lower or "custom" in t_lower or "gallery" in t_lower:
            reqs.append(
                RequirementItem(
                    id=f"REQ-{req_id:02d}",
                    title="Custom UI Widgets & Layout Enhancements",
                    description="Create upgrade-safe custom widgets in Developer Hub for custom badges, featured carousels, and header layouts.",
                    category=RequirementCategory.CUSTOM_CODE,
                    priority=PriorityLevel.SHOULD_HAVE,
                    complexity=ComplexityLevel.MEDIUM,
                    estimated_hours=8.0,
                    recommended_bd_addon="Widget Manager (Native)",
                )
            )
            req_id += 1

        # Out of scope items
        out_of_scope = [
            "Bespoke mobile app development (iOS/Android native binaries)",
            "Bidirectional EHR/ERP deep database syncing outside webhook payload",
            "Custom video conferencing / telemedicine infrastructure",
            "Manual phone outreach for member onboarding"
        ]

        # Technical Risks
        risks = [
            RiskItem(
                risk="Large database geocoding API rate limits during bulk import",
                impact="Potential timeout during CSV ingestion",
                mitigation="Segment data into 2,000-record batches and pre-populate lat/long coordinates."
            ),
            RiskItem(
                risk="Email deliverability to member spam folders",
                impact="Providers miss critical lead notifications",
                mitigation="Implement custom SMTP (SendGrid/Mailgun) with SPF and DKIM DNS authentication."
            )
        ]

        # Recommended BD Add-ons
        addons = [
            {"name": "Claim Listings Add-on", "justification": "Eliminates need for custom verification portal and auto-links Stripe payment."},
            {"name": "Automated Lead Routing Add-on", "justification": "Built-in radius geocoding and automated contractor lead distribution."},
            {"name": "Member Reviews Add-on", "justification": "Out-of-the-box star ratings, review moderation, and schema markup for Google SEO."}
        ]

        exec_summary = (
            f"Comprehensive platform implementation and launch of {meta.title} for {meta.client_company}, "
            "delivering tiered monetization, verified member listings, radial geocoding search, "
            "and automated customer inquiry routing on Brilliant Directories."
        )

        return DiscoveryAnalysis(
            meeting_id=meta.id,
            project_title=meta.title,
            client_name=meta.client_name,
            client_company=meta.client_company,
            executive_summary=exec_summary,
            business_model="Tiered recurring subscription membership & optional pay-per-lead credits",
            target_audience="Industry service providers and active public consumers seeking verified solutions",
            timeline_requested="6 to 8 weeks",
            requirements=reqs,
            out_of_scope=out_of_scope,
            technical_risks=risks,
            recommended_addons=addons,
        )
