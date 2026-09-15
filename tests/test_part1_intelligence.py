"""
tests/test_part1_intelligence.py - Verification suite for Sub-Part 1:
Core Intelligence, Trilingual Classification, and Organic Discovery.
"""

from core.classifier import LeadClassifier
from core.prompt import get_assistant_system_prompt
from core.tools_schema import TOOLS_SCHEMA


def test_system_prompt_configuration():
    """Verifies prompt contains target number, trilingual instructions, and anti-robotic rules."""
    prompt = get_assistant_system_prompt("+918790513762")
    assert "+918790513762" in prompt
    assert "Telugu" in prompt
    assert "Hindi" in prompt
    assert "English" in prompt
    assert "trigger_midcall_whatsapp" in prompt
    assert "schedule_callback" in prompt


def test_tools_schema_integrity():
    """Verifies tool definitions match required function calling signatures."""
    tool_names = [t["function"]["name"] for t in TOOLS_SCHEMA]
    assert "trigger_midcall_whatsapp" in tool_names
    assert "schedule_callback" in tool_names


def test_hot_intent_detection_and_extraction():
    """Verifies HOT lead with urgency and pricing query is correctly identified."""
    classifier = LeadClassifier()
    utterances = [
        "Hey Ananya, we sell organic cold-pressed oils, about 25 products.",
        "We need to launch within 2 weeks before Diwali. What is your pricing and how soon can you start?",
        "We also need Razorpay payment gateway and shipping integration."
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "HOT"
    assert result.extracted_data.product_type == "Food & Organic Products"
    assert result.extracted_data.sku_count == "25 items"
    assert "within 2 weeks" in result.extracted_data.timeline.lower()
    assert "Payment Gateway (Razorpay/COD)" in result.extracted_data.key_features
    assert "Automated Shipping Integration" in result.extracted_data.key_features
    assert "Trigger mid-call WhatsApp" in result.recommended_action


def test_warm_intent_decision_maker_barrier():
    """Verifies PDF scenario: 'my brother handles this'."""
    classifier = LeadClassifier()
    utterances = [
        "We have a jewelry shop and want to sell bangles online.",
        "Around 50 designs.",
        "Actually, my brother handles the technical decisions, can you talk to him?"
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "WARM"
    assert "brother" in result.barrier.lower()
    assert result.extracted_data.product_type == "Jewelry & Accessories"


def test_warm_intent_budget_barrier():
    """Verifies PDF scenario: 'my budget is not much right now'."""
    classifier = LeadClassifier()
    utterances = [
        "I sell designer kurtis from home.",
        "My budget is not much right now, maybe around 20k."
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "WARM"
    assert "budget" in result.barrier.lower()
    assert result.extracted_data.product_type == "Clothing & Fashion"


def test_warm_intent_timing_barrier():
    """Verifies PDF scenario: 'call me back tomorrow morning'."""
    classifier = LeadClassifier()
    utterances = [
        "I'm driving right now, call me back tomorrow morning."
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "WARM"
    assert "timing" in result.barrier.lower()
    assert "Schedule callback" in result.recommended_action


def test_cold_intent_detection():
    """Verifies caller with no need is marked COLD."""
    classifier = LeadClassifier()
    utterances = [
        "No no, I was just clicking randomly, not interested, no plan for any website."
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "COLD"
    assert "brochure" in result.recommended_action.lower()


def test_telugu_code_switching():
    """Verifies Telugu + English code-switching."""
    classifier = LeadClassifier()
    utterances = [
        "Namaskaram andi! Maaku clothing store undi, online ecommerce website kavali.",
        "Entha cost avtundi? Eppudu start chestaru?"
    ]
    result = classifier.classify(utterances)

    assert result.temperature == "HOT"
    assert result.extracted_data.language_used in ["te", "mixed"]
    assert "Trigger mid-call WhatsApp" in result.recommended_action


if __name__ == "__main__":
    print("Running intelligence tests directly...")
    test_system_prompt_configuration()
    test_tools_schema_integrity()
    test_hot_intent_detection_and_extraction()
    test_warm_intent_decision_maker_barrier()
    test_warm_intent_budget_barrier()
    test_warm_intent_timing_barrier()
    test_cold_intent_detection()
    test_telugu_code_switching()
    print("ALL TESTS PASSED SUCCESSFULLY!")
