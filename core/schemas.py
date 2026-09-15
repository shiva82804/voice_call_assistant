"""
core/schemas.py - Data contracts and Pydantic models for Voice Call Assistant.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field

LeadTemperature = Literal["HOT", "WARM", "COLD"]


class LeadDiscoveryData(BaseModel):
    """5 Core Qualification Dimensions parsed from the conversation."""
    product_type: Optional[str] = Field(
        default=None,
        description="Type of products the lead sells (e.g. fashion, electronics, organic food)"
    )
    sku_count: Optional[str] = Field(
        default=None,
        description="Number of products or collection size (e.g. 15-20 items, 500+ SKUs)"
    )
    timeline: Optional[str] = Field(
        default=None,
        description="Urgency/launch target (e.g. within 2 weeks, next month, festive season)"
    )
    budget: Optional[str] = Field(
        default=None,
        description="Stated budget or investment range (e.g. 30k-50k, tight budget, 1 Lakh)"
    )
    key_features: List[str] = Field(
        default_factory=list,
        description="Features requested (e.g. Razorpay, COD, automated shipping, mobile UI)"
    )
    language_used: Literal["en", "te", "hi", "mixed"] = Field(
        default="en",
        description="Primary language or mixed code-switching detected during the call"
    )


class LeadClassificationResult(BaseModel):
    """Evaluation result classifying lead temperature and deciding the next action."""
    temperature: Literal["HOT", "WARM", "COLD"] = Field(
        description="Lead classification: HOT (high intent), WARM (interested with barrier), COLD (just looking)"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Classification confidence score"
    )
    barrier: Optional[str] = Field(
        default=None,
        description="Identified hesitation for WARM leads (e.g. budget, timeline, decision maker)"
    )
    recommended_action: str = Field(
        description="Next immediate action: trigger mid-call WhatsApp, schedule callback, or log and brochure"
    )
    reasoning: str = Field(
        description="Explanation of why this classification was assigned based on caller utterances"
    )
    extracted_data: LeadDiscoveryData = Field(
        default_factory=LeadDiscoveryData,
        description="Discovery details extracted so far"
    )


class MidCallWhatsAppPayload(BaseModel):
    """Payload triggered asynchronously during the call for HOT leads."""
    phone_number: str = Field(
        default="+918790513762",
        description="Recipient phone number with country code"
    )
    interest_summary: str = Field(
        description="Short, contextual summary of what the lead is looking to build"
    )
    portfolio_category: Optional[str] = Field(
        default="e-commerce",
        description="Niche category to highlight relevant case studies"
    )


class CallbackSchedulePayload(BaseModel):
    """Payload triggered when caller requests a callback or has a timing barrier."""
    spoken_time_phrase: str = Field(
        description="Spoken time expression, e.g. 'tomorrow morning', 'Friday at 3pm'"
    )
    topic: str = Field(
        default="E-commerce website proposal discussion",
        description="Subject for the callback"
    )
    barrier_addressed: Optional[str] = Field(
        default=None,
        description="The objection or barrier to address during the callback"
    )
