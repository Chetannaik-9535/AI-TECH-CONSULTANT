"""
AI Tech Consultant - Meeting to Scope
Pydantic data models for transcripts, discovery analysis, and Scope of Work (SOW).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RequirementCategory(str, Enum):
    CORE_SETUP = "Core Setup & Configuration"
    FUNCTIONAL = "Functional Features"
    TECHNICAL_INTEGRATIONS = "Third-Party Integrations"
    CUSTOM_CODE = "Custom PHP / Widgets"
    DATA_MIGRATION = "Data Migration & Import"
    DESIGN_UX = "Design & Branding"
    EMAIL_DELIVERABILITY = "Email & Notifications"


class PriorityLevel(str, Enum):
    MUST_HAVE = "Must Have"
    SHOULD_HAVE = "Should Have"
    NICE_TO_HAVE = "Nice to Have"


class ComplexityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TranscriptUtterance(BaseModel):
    speaker: str
    timestamp: Optional[str] = None
    text: str


class MeetingMetadata(BaseModel):
    id: str
    title: str
    client_name: str
    client_company: str
    client_email: Optional[str] = None
    date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    duration_minutes: int = 45
    participants: list[str] = Field(default_factory=list)


class MeetingInput(BaseModel):
    metadata: MeetingMetadata
    transcript: str
    custom_notes: Optional[str] = None


class RequirementItem(BaseModel):
    id: str
    title: str
    description: str
    category: RequirementCategory
    priority: PriorityLevel = PriorityLevel.MUST_HAVE
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
    estimated_hours: float = 6.0
    recommended_bd_addon: Optional[str] = None


class RiskItem(BaseModel):
    risk: str
    impact: str
    mitigation: str


class DiscoveryAnalysis(BaseModel):
    meeting_id: str
    project_title: str
    client_name: str
    client_company: str
    executive_summary: str
    business_model: str
    target_audience: str
    timeline_requested: str
    budget_range: Optional[str] = None
    requirements: list[RequirementItem] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    technical_risks: list[RiskItem] = Field(default_factory=list)
    recommended_addons: list[dict] = Field(default_factory=list)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


class DeliverableItem(BaseModel):
    id: str
    title: str
    description: str
    estimated_hours: float


class ProjectPhase(BaseModel):
    phase_number: int
    phase_name: str
    description: str
    deliverables: list[DeliverableItem] = Field(default_factory=list)
    phase_hours: float
    phase_cost: float


class MilestoneItem(BaseModel):
    name: str
    target_week: int
    deliverable_summary: str
    payment_percentage: int


class ScopeOfWork(BaseModel):
    sow_id: str
    meeting_id: str
    project_title: str
    client_name: str
    client_company: str
    date_generated: str = Field(default_factory=lambda: datetime.utcnow().strftime("%B %d, %Y"))
    executive_summary: str
    phases: list[ProjectPhase] = Field(default_factory=list)
    total_hours: float
    hourly_rate: float = 150.0
    total_cost: float
    timeline_weeks: int
    milestones: list[MilestoneItem] = Field(default_factory=list)
    recommended_addons: list[dict] = Field(default_factory=list)
    client_responsibilities: list[str] = Field(default_factory=list)
    markdown_document: str = ""
