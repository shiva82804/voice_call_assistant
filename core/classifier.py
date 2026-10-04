"""
core/classifier.py - Rule-based and semantic intent classifier for live conversation analysis.
Evaluates caller responses into HOT, WARM, or COLD leads, extracting the 5 discovery dimensions,
identifying barriers, and recommending immediate real-time actions.
"""

import re
from typing import List, Optional, Tuple
from .schemas import LeadDiscoveryData, LeadClassificationResult, LeadTemperature


class LeadClassifier:
    """Classifies conversation state and extracts structured lead discovery data."""

    # Keywords for intent detection
    HOT_SIGNALS = [
        r"how soon can you (start|deliver|launch|build)",
        r"when can (we|you) start",
        r"how much (does it cost|will it cost|is it)",
        r"(what is|tell me) (the |your )?pricing",
        r"send (me )?(the )?(proposal|quote|details|pricing|portfolio) (right now|now|immediately)",
        r"ready to start",
        r"budget is around",
        r"entha (avtundi|cost|charge chestaru)",       # Telugu: how much will it cost
        r"eppudu start chestaru",                      # Telugu: when will you start
        r"details pampandi",                           # Telugu: send details
        r"kitna (kharcha|charge|paisa|cost) lagega",   # Hindi: how much will it cost
        r"kab start (kar sakte|hoga)",                 # Hindi: when can we start
        r"proposal bhej do",                           # Hindi: send proposal
    ]

    WARM_BUDGET_BARRIERS = [
        r"budget is not much",
        r"budget is tight",
        r"don't have (much|enough) budget",
        r"budget konchem (tight|problem|takkuva)",     # Telugu
        r"budget kam hai",                             # Hindi
        r"zyada budget nahi hai",                      # Hindi
        r"thoda mehenga",                              # Hindi
    ]

    WARM_DECISION_BARRIERS = [
        r"(my )?(brother|partner|father|boss|team|director) handles",
        r"need to (ask|discuss with|check with) (my )?(brother|partner|father|boss|team)",
        r"(talk|speak) to (my )?(brother|partner|father|boss|him|her)",
        r"decision maker",
        r"partner tho (matladali|discuss cheyali)",    # Telugu
        r"ma brother chustadu",                        # Telugu
        r"bhaiya (se baat|se poochna)",                # Hindi
        r"partner se discuss karna",                   # Hindi
    ]

    WARM_TIMING_BARRIERS = [
        r"call (me )?back (tomorrow|later|next week|in the evening|morning|afternoon)",
        r"busy right now",
        r"in a meeting",
        r"driving right now",
        r"tarvata call cheyyandi",                     # Telugu
        r"repu (morning|afternoon|matladam)",          # Telugu
        r"kal call karo",                              # Hindi
        r"baad mein baat karte hain",                  # Hindi
    ]

    COLD_SIGNALS = [
        r"just (looking|browsing|checking)",
        r"not interested",
        r"no (need|plan|requirement|budget)",
        r"accidentally clicked",
        r"wrong number",
        r"bore kottindi",                              # Telugu
        r"avsaram ledu",                               # Telugu
        r"zaroorat nahi hai",                          # Hindi
        r"koi plan nahi hai",                          # Hindi
    ]

    # Language markers
    TELUGU_MARKERS = [
        r"\b(namaskaram|andi|nenu|kavali|avtundi|cheyyandi|eppudu|repu|tarvata|chustunna|cheddam|leda)\b"
    ]
    HINDI_MARKERS = [
        r"\b(namaste|haan|nahi|chahiye|batao|karo|baat|hoga|karna|shuru|bhaiya|humara|mujhe)\b"
    ]

    def detect_language(self, text: str) -> str:
        """Detects whether text is predominantly English, Telugu, Hindi, or mixed."""
        text_lower = text.lower()
        has_te = any(re.search(p, text_lower) for p in self.TELUGU_MARKERS)
        has_hi = any(re.search(p, text_lower) for p in self.HINDI_MARKERS)
        has_en = bool(re.search(r"\b(website|ecommerce|store|online|budget|products|deliver|start)\b", text_lower))

        if (has_te and has_en) or (has_hi and has_en):
            return "mixed"
        if has_te:
            return "te"
        if has_hi:
            return "hi"
        return "en"

    def extract_discovery_data(self, conversation_history: List[str]) -> LeadDiscoveryData:
        """Extracts the 5 discovery dimensions from conversation transcript lines."""
        combined_text = " ".join(conversation_history).lower()
        data = LeadDiscoveryData()

        data.language_used = self.detect_language(combined_text)

        # 1. Product Niche
        product_patterns = [
            (r"(clothing|apparel|sarees|kurtis|fashion|dresses)", "Clothing & Fashion"),
            (r"(jewelry|jewellery|bangles|accessories)", "Jewelry & Accessories"),
            (r"(organic|oils|ghee|food|spices|snacks|honey)", "Food & Organic Products"),
            (r"(electronics|gadgets|mobiles|chargers)", "Electronics & Gadgets"),
            (r"(shoes|footwear|leather)", "Footwear & Leather Goods"),
            (r"(cosmetics|skincare|beauty|soaps)", "Beauty & Skincare"),
        ]
        for pattern, label in product_patterns:
            if re.search(pattern, combined_text):
                data.product_type = label
                break

        # 2. SKU Count
        sku_match = re.search(r"(\d+)\s*(products|skus|items|designs|varieties|collection)", combined_text)
        if sku_match:
            data.sku_count = f"{sku_match.group(1)} items"
        elif re.search(r"(small collection|focused collection|15-20|10-20)", combined_text):
            data.sku_count = "15-25 items"
        elif re.search(r"(large catalog|100\+|many products|500\+)", combined_text):
            data.sku_count = "100+ items"

        # 3. Timeline
        timeline_match = re.search(r"((?:within|in)\s+\d+\s+weeks?|in \d+ days?|next month|diwali|urgently|asap|2 weeks|next week)", combined_text)
        if timeline_match:
            data.timeline = timeline_match.group(0)

        # 4. Budget
        budget_match = re.search(r"(around|about|budget is|under)?\s*(rs\.?|inr|₹)?\s*(\d+k|\d+,\d+|\d+\s*thousand|\d+\s*lakh)", combined_text)
        if budget_match:
            data.budget = budget_match.group(0).strip()
        elif any(re.search(p, combined_text) for p in self.WARM_BUDGET_BARRIERS):
            data.budget = "Tight / Constrained Budget"

        # 5. Features
        features = []
        if re.search(r"(razorpay|payment gateway|cod|cash on delivery|payments)", combined_text):
            features.append("Payment Gateway (Razorpay/COD)")
        if re.search(r"(shipping|courier|delivery tracking|shiprocket)", combined_text):
            features.append("Automated Shipping Integration")
        if re.search(r"(custom design|mobile ui|clean design|responsive)", combined_text):
            features.append("Mobile-Optimized Custom UI")
        if re.search(r"(instagram|social media|whatsapp chat)", combined_text):
            features.append("WhatsApp / Social Integration")
        data.key_features = features

        return data

    def classify(self, caller_utterances: List[str]) -> LeadClassificationResult:
        """Classifies the caller's intent and decides the immediate action."""
        full_text = " ".join(caller_utterances).lower()
        extracted_data = self.extract_discovery_data(caller_utterances)

        # Priority 1: Check COLD signals
        is_cold = any(re.search(p, full_text) for p in self.COLD_SIGNALS)
        if is_cold and not any(re.search(p, full_text) for p in self.HOT_SIGNALS):
            return LeadClassificationResult(
                temperature="COLD",
                confidence=0.90,
                barrier="No active need or budget",
                recommended_action="Polite wrap-up, log record, offer brochure via WhatsApp",
                reasoning="Caller explicitly indicated no need, casual browsing, or lack of interest.",
                extracted_data=extracted_data
            )

        # Priority 2: Check HOT buying intent
        is_hot = any(re.search(p, full_text) for p in self.HOT_SIGNALS)
        has_strong_discovery = (extracted_data.product_type is not None and 
                                (extracted_data.timeline is not None or extracted_data.budget is not None))

        if is_hot or (has_strong_discovery and "how soon" in full_text):
            return LeadClassificationResult(
                temperature="HOT",
                confidence=0.95,
                barrier=None,
                recommended_action="Trigger mid-call WhatsApp immediately with portfolio/proposal",
                reasoning="Caller displayed high buying intent, asked for pricing/timeline/immediate details.",
                extracted_data=extracted_data
            )

        # Priority 3: Check WARM with Barriers
        for pattern in self.WARM_DECISION_BARRIERS:
            if re.search(pattern, full_text):
                return LeadClassificationResult(
                    temperature="WARM",
                    confidence=0.90,
                    barrier="Decision maker barrier (partner/brother/boss)",
                    recommended_action="Acknowledge authority, schedule joint callback",
                    reasoning="Lead is interested but must consult another decision maker.",
                    extracted_data=extracted_data
                )

        for pattern in self.WARM_BUDGET_BARRIERS:
            if re.search(pattern, full_text):
                return LeadClassificationResult(
                    temperature="WARM",
                    confidence=0.88,
                    barrier="Budget constraint",
                    recommended_action="Propose starter/MVP build, schedule callback",
                    reasoning="Real e-commerce requirement exists but with budget sensitivity.",
                    extracted_data=extracted_data
                )

        for pattern in self.WARM_TIMING_BARRIERS:
            if re.search(pattern, full_text):
                return LeadClassificationResult(
                    temperature="WARM",
                    confidence=0.92,
                    barrier="Timing constraint / Busy now",
                    recommended_action="Schedule callback for specified time",
                    reasoning="Caller requested callback at another time.",
                    extracted_data=extracted_data
                )

        # Default fallback based on discovery richness
        if extracted_data.product_type:
            return LeadClassificationResult(
                temperature="WARM",
                confidence=0.75,
                barrier="Exploring options",
                recommended_action="Share portfolio and schedule follow-up",
                reasoning="Caller engaged in discovery discussion about their store.",
                extracted_data=extracted_data
            )

        return LeadClassificationResult(
            temperature="WARM",
            confidence=0.60,
            barrier="Early stage discussion",
            recommended_action="Continue consultative qualification",
            reasoning="Insufficient signals for strong HOT or COLD determination.",
            extracted_data=extracted_data
        )
