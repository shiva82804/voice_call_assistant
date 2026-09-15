"""
tests/test_part6_post_call.py - Verification of Sub-Part 6:
Post-call synthesis, human framing, and rich WhatsApp delivery.
"""

from services.post_call_processor import PostCallProcessor
from services.whatsapp_service import WhatsAppService


def test_post_call_synthesis_and_formatting():
    """Verifies that transcript specifics are correctly extracted and humanly framed."""
    processor = PostCallProcessor()
    transcript = [
        "Assistant: Hey there! This is Ananya from ElevateBox. What kind of products are you planning to sell?",
        "Lead: We make handmade silver jewelry, about 35 designs.",
        "Assistant: Love it! For jewelry, do you need payment gateway like Razorpay?",
        "Lead: Yes, Razorpay and COD. We want to launch in 3 weeks before Diwali. Budget is around 40k."
    ]

    result = processor.process_and_dispatch(
        conversation_transcript=transcript,
        recipient_phone="+918790513762"
    )

    assert result["status"] == "completed"
    assert result["extracted_discovery"]["product_type"] == "Jewelry & Accessories"
    assert "35 items" in result["extracted_discovery"]["sku_count"]
    assert "in 3 weeks" in result["extracted_discovery"]["timeline"]

    # Verify message framing
    message_text = processor.format_human_followup_message(
        processor.classifier.extract_discovery_data(transcript),
        recipient_phone="+918790513762"
    )
    assert "Jewelry & Accessories" in message_text
    assert "35 items" in message_text
    assert "Razorpay" in message_text
    assert "+918790513762" in message_text  # Candidate number must be visible


if __name__ == "__main__":
    print("Running post-call synthesis tests...")
    test_post_call_synthesis_and_formatting()
    print("ALL POST-CALL SYNTHESIS TESTS PASSED!")
