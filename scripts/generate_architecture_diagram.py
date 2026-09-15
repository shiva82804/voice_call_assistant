"""
scripts/generate_architecture_diagram.py - Generates a crisp, high-resolution visual
architecture diagram (PNG) to be automatically sent as a WhatsApp attachment.
Fulfills ElevateBox Requirement Section 06 (Item 4).
"""

import os
from PIL import Image, ImageDraw, ImageFont


def generate_architecture_image(output_path: str = "assets/architecture_diagram.png"):
    """Renders a clean, modern system architecture diagram image."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Canvas dimensions
    width, height = 1200, 850
    img = Image.new("RGB", (width, height), color="#0F172A")  # Deep Slate Dark
    draw = ImageDraw.Draw(img)

    # Load default fonts
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_subtitle = ImageFont.truetype("arial.ttf", 20)
        font_header = ImageFont.truetype("arial.ttf", 22)
        font_body = ImageFont.truetype("arial.ttf", 16)
        font_badge = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # 1. Header Banner
    draw.text((60, 40), "ElevateBox AI Voice Assistant - Architecture Flow", fill="#38BDF8", font=font_title)
    draw.text((60, 85), "End-to-End Autonomous Outbound Calling, Intent Classification & Mid-Call Execution", fill="#94A3B8", font=font_subtitle)

    # Divider line
    draw.line([(60, 125), (width - 60, 125)], fill="#334155", width=2)

    # Boxes definitions: (x, y, w, h, title, subtitle, bullets, border_color, fill_color)
    modules = [
        {
            "rect": (60, 150, 320, 200),
            "title": "1. Telephony & Audio Stream",
            "tag": "Voice Gateway",
            "bullets": [
                "• Outbound Dialing (+91 8790513762)",
                "• Vapi / Twilio SIP Trunking",
                "• Low-Latency Full Duplex Audio",
                "• Barge-in & Interruption Cutoff",
                "• Ambient Room Noise Injected"
            ],
            "accent": "#38BDF8"
        },
        {
            "rect": (440, 150, 320, 200),
            "title": "2. Speech & Voice Pipeline",
            "tag": "< 1.2s Roundtrip",
            "bullets": [
                "• STT: Deepgram / Soniox Nova-2",
                "• Telugu, Hindi & English Speech",
                "• Mixed Sentences (Tenglish/Hinglish)",
                "• TTS: Cartesia / ElevenLabs v2",
                "• Natural Indian Female Voice"
            ],
            "accent": "#818CF8"
        },
        {
            "rect": (820, 150, 320, 200),
            "title": "3. Conversation Brain (LLM)",
            "tag": "GPT-4o Consultant",
            "bullets": [
                "• Consultative Persona: Ananya",
                "• Organic 5-Dimension Discovery",
                "• Piggybacking on Spoken Info",
                "• < 25 Words / Turn Pacing",
                "• Real-Time Function Calling"
            ],
            "accent": "#34D399"
        },
        {
            "rect": (60, 400, 320, 210),
            "title": "4. Intent Classifier Matrix",
            "tag": "Decision Engine",
            "bullets": [
                "• HOT: Urgency, pricing, timeline",
                "  -> Fires WhatsApp Mid-Call!",
                "• WARM: Budget/Decision barriers",
                "  -> Offers MVP, books callback",
                "• COLD: No budget/curious only",
                "  -> Polite wrap-up & brochure"
            ],
            "accent": "#F59E0B"
        },
        {
            "rect": (440, 400, 320, 210),
            "title": "5. IST Callback Scheduler",
            "tag": "Spoken Time Parser",
            "bullets": [
                "• Parses Colloquial Expressions:",
                "  'Tomorrow morning' -> 10 AM IST",
                "  'Day after at 3pm' -> 15:00 IST",
                "  'Repu morning 11 ki' (Telugu)",
                "  'Kal subah 10 baje' (Hindi)",
                "• Persisted JSON / Calendar sync"
            ],
            "accent": "#EC4899"
        },
        {
            "rect": (820, 400, 320, 210),
            "title": "6. WhatsApp Delivery Layer",
            "tag": "Multi-Provider Engine",
            "bullets": [
                "• Meta Cloud / Twilio API",
                "• Mid-Call Intent Alert (Async)",
                "• Post-Call Contextual Recap",
                "• Architecture Diagram (PNG)",
                "• Candidate Resume (PDF)"
            ],
            "accent": "#10B981"
        }
    ]

    for mod in modules:
        x, y, w, h = mod["rect"]
        accent = mod["accent"]

        # Background card
        draw.rounded_rectangle([x, y, x + w, y + h], radius=12, fill="#1E293B", outline="#334155", width=2)
        # Accent top bar
        draw.rounded_rectangle([x, y, x + w, y + 6], radius=3, fill=accent)

        # Title & Badge
        draw.text((x + 16, y + 16), mod["title"], fill="#F8FAFC", font=font_header)
        draw.text((x + 16, y + 42), mod["tag"].upper(), fill=accent, font=font_badge)

        # Bullets
        cur_y = y + 70
        for b in mod["bullets"]:
            draw.text((x + 16, cur_y), b, fill="#CBD5E1", font=font_body)
            cur_y += 24

    # Connecting Flow Arrows / Indicators
    draw.line([(380, 250), (440, 250)], fill="#64748B", width=3)
    draw.polygon([(435, 245), (445, 250), (435, 255)], fill="#64748B")

    draw.line([(760, 250), (820, 250)], fill="#64748B", width=3)
    draw.polygon([(815, 245), (825, 250), (815, 255)], fill="#64748B")

    draw.line([(980, 350), (980, 400)], fill="#64748B", width=3)
    draw.polygon([(975, 395), (980, 405), (985, 395)], fill="#64748B")

    draw.line([(820, 505), (760, 505)], fill="#64748B", width=3)
    draw.polygon([(765, 500), (755, 505), (765, 510)], fill="#64748B")

    draw.line([(440, 505), (380, 505)], fill="#64748B", width=3)
    draw.polygon([(385, 500), (375, 505), (385, 510)], fill="#64748B")

    # Bottom Footer Box (Follow-up guarantee)
    footer_rect = [60, 645, width - 60, 805]
    draw.rounded_rectangle(footer_rect, radius=12, fill="#0F243E", outline="#0284C7", width=2)
    draw.text((85, 665), "LIVE DEMO & POST-CALL DELIVERY GUARANTEE", fill="#38BDF8", font=font_header)
    draw.text(
        (85, 700),
        "1. Active Call: Dials +91 8790513762 | 2. Mid-Call: Fires WhatsApp upon HOT intent while still talking\n"
        "3. Post-Call: Evaluates full transcript -> sends human summary + candidate number + resume + architecture\n"
        "Engineered for sub-second latency, barge-in resilience, and trilingual fluency (Telugu, Hindi, English).",
        fill="#E2E8F0",
        font=font_body
    )

    img.save(output_path, "PNG")
    print(f"Architecture diagram generated successfully at: {output_path}")


if __name__ == "__main__":
    generate_architecture_image()
