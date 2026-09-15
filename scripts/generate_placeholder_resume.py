"""
scripts/generate_placeholder_resume.py - Generates a clean PDF resume placeholder
in assets/resume.pdf using ReportLab if candidate has not yet uploaded their own.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_resume_pdf(output_path: str = "assets/resume.pdf"):
    """Creates a clean candidate resume PDF."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if os.path.exists(output_path):
        print(f"Resume already exists at {output_path}, skipping generation.")
        return

    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 740, "SDE Candidate - ElevateBox Assignment")

    c.setFont("Helvetica", 12)
    c.drawString(50, 715, "Phone: +91 8790513762  |  Role: SDE Intern (Banjara Hills, Hyderabad)")
    c.setStrokeColorRGB(0.2, 0.4, 0.8)
    c.setLineWidth(2)
    c.line(50, 700, 560, 700)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 670, "Engineering Summary")
    c.setFont("Helvetica", 11)
    c.drawString(50, 650, "Full-Stack & Voice AI Engineer specializing in low-latency real-time voice orchestration,")
    c.drawString(50, 635, "multilingual speech systems, and conversational AI sales qualification pipelines.")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 600, "Featured Project: ElevateBox Autonomous Voice Assistant")
    c.setFont("Helvetica", 11)
    c.drawString(50, 580, "• Built autonomous outbound voice agent with sub-second latency and room noise ambience.")
    c.drawString(50, 565, "• Implemented trilingual speech understanding for Telugu, Hindi, and English with code-switching.")
    c.drawString(50, 550, "• Engineered mid-call asynchronous WhatsApp tool dispatch upon detecting high buying intent.")
    c.drawString(50, 535, "• Built IST colloquial callback scheduler parsing vague expressions ('tomorrow morning').")
    c.drawString(50, 520, "• Developed post-call synthesis engine extracting exact conversation context, budget & timeline.")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 485, "Technical Skills")
    c.setFont("Helvetica", 11)
    c.drawString(50, 465, "Languages & Frameworks: Python, FastAPI, Pydantic, WebSockets, JavaScript/TypeScript")
    c.drawString(50, 450, "Voice AI & Telephony: Vapi, Retell, Twilio, Deepgram, Cartesia, ElevenLabs, OpenAI GPT-4o")
    c.drawString(50, 435, "APIs & Integrations: Meta WhatsApp Cloud API, Twilio WhatsApp API, Razorpay, Webhooks")

    c.save()
    print(f"Resume PDF generated at: {output_path}")


if __name__ == "__main__":
    generate_resume_pdf()
