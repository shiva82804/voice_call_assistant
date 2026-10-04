"""
services/post_call_processor.py - Synthesizes completed call transcripts,
generates a human-framed contextual follow-up, and coordinates WhatsApp follow-up delivery.
"""

import os
from typing import List, Dict, Any, Optional
from core.classifier import LeadClassifier
from core.schemas import LeadDiscoveryData
from services.whatsapp_service import WhatsAppService


class PostCallProcessor:
    """Processes call transcript, creates human follow-up, and dispatches rich WhatsApp package."""

    def __init__(self, whatsapp_service: Optional[WhatsAppService] = None):
        self.whatsapp_service = whatsapp_service or WhatsAppService()
        self.classifier = LeadClassifier()
        self.contact_phone = os.getenv("CONTACT_PHONE", os.getenv("CONSULTANT_PHONE", "+918790513762"))
        self.consultant_name = os.getenv("CONSULTANT_NAME", "Ananya")

    def format_human_followup_message(
        self,
        discovery: LeadDiscoveryData,
        recipient_phone: str
    ) -> str:
        """
        Formats a human consultant follow-up message referencing exact call specifics:
        - Real specifics (product, SKU, timeline, budget, features).
        - Human framing (not a raw database log).
        - Direct consultant contact number.
        """
        products = discovery.product_type or "e-commerce catalog"
        skus = discovery.sku_count or "initial launch collection"
        timeline = discovery.timeline or "your upcoming launch window"
        budget = discovery.budget or "flexible based on scope"
        features_str = ", ".join(discovery.key_features) if discovery.key_features else "Razorpay payment gateway, mobile-first design, and order tracking"

        msg = (
            f"Hi! This is Ananya following up right after our call. 🚀\n\n"
            f"It was great speaking with you about getting your {products} store launched online ({skus}).\n\n"
            f"Here is a quick recap of the specifics we discussed:\n"
            f"• Scope: {products} ({skus})\n"
            f"• Target Timeline: {timeline}\n"
            f"• Budget Range: {budget}\n"
            f"• Key Requirements: {features_str}\n\n"
            f"As discussed, I have attached:\n"
            f"📊 Our Architecture & Flow Diagram (showing how this voice pipeline operates)\n\n"
            f"You can call or text back directly on:\n"
            f"📞 {self.contact_phone}\n\n"
            f"Excited to work together,\n"
            f"{self.consultant_name}"
        )
        return msg

    def process_and_dispatch(
        self,
        conversation_transcript: List[str],
        recipient_phone: str = "+918790513762",
        diagram_path: str = "assets/architecture_diagram.png"
    ) -> Dict[str, Any]:
        """
        Full post-call pipeline:
        1. Synthesizes transcript into structured discovery points.
        2. Formats natural human message.
        3. Dispatches text message with contact details.
        4. Dispatches architecture diagram.
        """
        # 1. Extract specifics
        discovery = self.classifier.extract_discovery_data(conversation_transcript)

        # 2. Format human message
        followup_text = self.format_human_followup_message(discovery, recipient_phone)

        # 3. Dispatch text message
        text_res = self.whatsapp_service.send_text_message(recipient_phone, followup_text)

        # 4. Dispatch architecture diagram
        diagram_res = {}
        if os.path.exists(diagram_path):
            diagram_caption = "📊 System Architecture: Real-time outbound telephony, multilingual speech, and intent decision engine."
            diagram_res = self.whatsapp_service.send_media_message(
                recipient_phone=recipient_phone,
                caption=diagram_caption,
                media_url_or_path=diagram_path,
                media_type="image"
            )

        return {
            "status": "completed",
            "recipient": recipient_phone,
            "extracted_discovery": discovery.model_dump(),
            "text_dispatch": text_res,
            "diagram_dispatch": diagram_res
        }
