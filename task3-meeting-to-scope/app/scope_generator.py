"""
AI Tech Consultant - Meeting to Scope
Generates phased Scope of Work (SOW), estimates, milestones, and client-ready Markdown.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.config import get_settings
from app.models import (
    DiscoveryAnalysis, ScopeOfWork, ProjectPhase, DeliverableItem,
    MilestoneItem, RequirementCategory,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ScopeGenerator:
    """Transforms discovery analysis into an executive Scope of Work document."""

    def __init__(self, hourly_rate: float = settings.default_hourly_rate):
        self.hourly_rate = hourly_rate

    def generate_sow(self, analysis: DiscoveryAnalysis, custom_rate: Optional[float] = None) -> ScopeOfWork:
        """Construct full Scope of Work from discovery requirements."""
        rate = custom_rate if custom_rate is not None else self.hourly_rate
        sow_id = f"SOW-{analysis.meeting_id.replace('MEET-', '')}-{datetime.utcnow().strftime('%y%m%d')}"

        # Group requirements into 4 phases
        phase1_delivs: list[DeliverableItem] = [
            DeliverableItem(
                id="DELIV-1.1",
                title="Brilliant Directories Core Environment Provisioning & Domain Setup",
                description="Configure SSL certificate, connect custom domain DNS records, and initialize baseline directory system tables.",
                estimated_hours=6.0,
            ),
            DeliverableItem(
                id="DELIV-1.2",
                title="Design System, Responsive Branding & Global Header/Footer",
                description="Implement client brand identity, customized color tokens, mobile responsive layouts, and typography.",
                estimated_hours=10.0,
            ),
        ]

        phase2_delivs: list[DeliverableItem] = []
        phase3_delivs: list[DeliverableItem] = []
        phase4_delivs: list[DeliverableItem] = [
            DeliverableItem(
                id="DELIV-4.1",
                title="End-to-End User Journey QA & Browser Compatibility Testing",
                description="Cross-device testing (Chrome, Safari iOS, Firefox, Android) across member signup, search filters, and checkout.",
                estimated_hours=8.0,
            ),
            DeliverableItem(
                id="DELIV-4.2",
                title="Admin Training, Documentation & DNS Production Cutover",
                description="Recorded admin training session for directory moderation, coupon codes, member management, and go-live launch.",
                estimated_hours=6.0,
            ),
        ]

        # Allocate requirements to Phase 2 (features) and Phase 3 (data & integrations)
        for req in analysis.requirements:
            deliv = DeliverableItem(
                id=f"DELIV-{req.id}",
                title=req.title,
                description=f"{req.description} (Recommended: {req.recommended_bd_addon or 'Native BD configuration'})",
                estimated_hours=req.estimated_hours,
            )

            if req.category in (RequirementCategory.DATA_MIGRATION, RequirementCategory.TECHNICAL_INTEGRATIONS):
                phase3_delivs.append(deliv)
            else:
                phase2_delivs.append(deliv)

        # Fallbacks if list is empty
        if not phase2_delivs:
            phase2_delivs.append(
                DeliverableItem(
                    id="DELIV-2.1",
                    title="Membership Plan & Directory Categories Setup",
                    description="Configure pricing plans, member search hierarchy, and contact forms.",
                    estimated_hours=14.0,
                )
            )

        if not phase3_delivs:
            phase3_delivs.append(
                DeliverableItem(
                    id="DELIV-3.1",
                    title="Member Data Import & Geocoded Location Mapping",
                    description="CSV ingestion, latitude/longitude geocoding, and payment gateway connection.",
                    estimated_hours=12.0,
                )
            )

        # Construct Phases
        def make_phase(num: int, name: str, desc: str, delivs: list[DeliverableItem]) -> ProjectPhase:
            hrs = sum(d.estimated_hours for d in delivs)
            return ProjectPhase(
                phase_number=num,
                phase_name=name,
                description=desc,
                deliverables=delivs,
                phase_hours=hrs,
                phase_cost=round(hrs * rate, 2),
            )

        phases = [
            make_phase(
                1,
                "Phase 1: Environment Provisioning, Brand Design & Architecture",
                "Foundation setup, domain routing, responsive CSS themes, and primary layouts.",
                phase1_delivs,
            ),
            make_phase(
                2,
                "Phase 2: Custom Functionality, Membership Monetization & Workflows",
                "Custom fields, search filters, Stripe subscription gateways, and claim listing moderation.",
                phase2_delivs,
            ),
            make_phase(
                3,
                "Phase 3: Data Migration, Third-Party Webhooks & Automation",
                "Database cleansing, geocoded member batch import, Twilio/SendGrid webhooks, and reviews.",
                phase3_delivs,
            ),
            make_phase(
                4,
                "Phase 4: Quality Assurance, Security Audit, Training & Launch",
                "Comprehensive cross-device validation, admin team training, and production cutover.",
                phase4_delivs,
            ),
        ]

        total_hours = sum(p.phase_hours for p in phases)
        total_cost = round(total_hours * rate, 2)
        timeline_weeks = max(4, int(total_hours // 10) + 1)

        # Milestones
        milestones = [
            MilestoneItem(
                name="Milestone 1: Project Initiation & Architecture Sign-Off",
                target_week=1,
                deliverable_summary="Environment created, domain DNS pointed, theme wireframes approved.",
                payment_percentage=40,
            ),
            MilestoneItem(
                name="Milestone 2: Functional Features & Migration Beta",
                target_week=max(2, timeline_weeks // 2),
                deliverable_summary="Membership plans active, Stripe test checkout, and batch data imported.",
                payment_percentage=30,
            ),
            MilestoneItem(
                name="Milestone 3: Final Acceptance & Public Launch",
                target_week=timeline_weeks,
                deliverable_summary="QA testing completed, admin training delivered, DNS cutover to live domain.",
                payment_percentage=30,
            ),
        ]

        # Client responsibilities
        responsibilities = [
            "Provide high-resolution vector logos, color codes, and brand imagery assets.",
            "Supply clean source CSV/Excel member data with column definitions.",
            "Grant access to domain registrar (DNS records) and third-party gateway accounts (Stripe, Twilio, SendGrid).",
            "Perform timely milestone review approvals within 3 business days of deliverable handoff.",
        ]

        # Generate comprehensive markdown document
        md_doc = self._generate_markdown(
            sow_id=sow_id,
            analysis=analysis,
            phases=phases,
            total_hours=total_hours,
            rate=rate,
            total_cost=total_cost,
            timeline_weeks=timeline_weeks,
            milestones=milestones,
            responsibilities=responsibilities,
        )

        return ScopeOfWork(
            sow_id=sow_id,
            meeting_id=analysis.meeting_id,
            project_title=analysis.project_title,
            client_name=analysis.client_name,
            client_company=analysis.client_company,
            executive_summary=analysis.executive_summary,
            phases=phases,
            total_hours=total_hours,
            hourly_rate=rate,
            total_cost=total_cost,
            timeline_weeks=timeline_weeks,
            milestones=milestones,
            recommended_addons=analysis.recommended_addons,
            client_responsibilities=responsibilities,
            markdown_document=md_doc,
        )

    def _generate_markdown(
        self,
        sow_id: str,
        analysis: DiscoveryAnalysis,
        phases: list[ProjectPhase],
        total_hours: float,
        rate: float,
        total_cost: float,
        timeline_weeks: int,
        milestones: list[MilestoneItem],
        responsibilities: list[str],
    ) -> str:
        """Render formal client Scope of Work document in Markdown."""
        date_str = datetime.utcnow().strftime("%B %d, %Y")

        md = []
        md.append(f"# Scope of Work (SOW): {analysis.project_title}")
        md.append(f"**Document Reference:** `{sow_id}` | **Date:** {date_str}  ")
        md.append(f"**Client:** {analysis.client_name} ({analysis.client_company})  ")
        md.append(f"**Consultant:** AI Tech Consultant Solutions Group  ")
        md.append(f"**Target Ecosystem:** Brilliant Directories Enterprise Platform  \n")
        md.append("---\n")

        md.append("## 1. Executive Summary & Project Objectives")
        md.append(f"{analysis.executive_summary}\n")
        md.append(f"- **Business Model:** {analysis.business_model}")
        md.append(f"- **Target Audience:** {analysis.target_audience}")
        md.append(f"- **Target Delivery Window:** {timeline_weeks} Weeks (Client goal: {analysis.timeline_requested})\n")

        md.append("## 2. Phased Project Deliverables & Effort Breakdown\n")

        for phase in phases:
            md.append(f"### {phase.phase_name}")
            md.append(f"*{phase.description}*\n")
            md.append("| Deliverable Ref | Deliverable Item & Description | Estimated Hours | Subtotal |")
            md.append("|:---|:---|:---:|:---:|")
            for d in phase.deliverables:
                cost_deliv = f"${d.estimated_hours * rate:,.2f}"
                md.append(f"| `{d.id}` | **{d.title}**<br>{d.description} | {d.estimated_hours:.1f} hrs | {cost_deliv} |")
            md.append(f"| **Subtotal** | | **{phase.phase_hours:.1f} hrs** | **${phase.phase_cost:,.2f}** |\n")

        md.append("## 3. Total Investment & Timeline Summary\n")
        md.append(f"- **Total Estimated Consulting Effort:** `{total_hours:.1f} hours`")
        md.append(f"- **Standard Consulting Rate:** `${rate:,.2f}/hour`")
        md.append(f"- **Total Project Investment:** **`${total_cost:,.2f}`**")
        md.append(f"- **Project Duration:** `{timeline_weeks} Weeks` from contract execution\n")

        md.append("## 4. Milestone Schedule & Payment Terms\n")
        md.append("| Milestone | Target Week | Deliverables Covered | Payment % | Amount |")
        md.append("|:---|:---:|:---|:---:|:---:|")
        for m in milestones:
            amt = (m.payment_percentage / 100.0) * total_cost
            md.append(f"| **{m.name}** | Week {m.target_week} | {m.deliverable_summary} | {m.payment_percentage}% | ${amt:,.2f} |")
        md.append("\n")

        if analysis.recommended_addons:
            md.append("## 5. Recommended Brilliant Directories Native Add-ons")
            md.append("To minimize bespoke development costs and ensure upgrade safety, the following native platform add-ons are specified:")
            for a in analysis.recommended_addons:
                md.append(f"- **{a.get('name', 'Add-on')}**: {a.get('justification', '')}")
            md.append("\n")

        md.append("## 6. Out of Scope (Project Boundaries)")
        md.append("The following items are explicitly excluded from this Phase 1 Scope of Work to maintain delivery schedule:")
        for oos in analysis.out_of_scope:
            md.append(f"- {oos}")
        md.append("\n")

        md.append("## 7. Assumptions & Client Responsibilities")
        for resp in responsibilities:
            md.append(f"- {resp}")
        md.append("\n")

        md.append("## 8. Change Order & Acceptance Terms")
        md.append("Any modifications, additions, or changes to the deliverables outlined above will be managed via a formal written Change Order. Deliverables are considered accepted if no written revisions are requested within 5 business days of demonstration.")
        md.append("\n---\n")
        md.append("*Prepared with precision by AI Tech Consultant for Brilliant Directories.*")

        return "\n".join(md)
