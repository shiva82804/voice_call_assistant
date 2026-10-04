"""
tests/test_server_webhooks.py - Integration tests for FastAPI webhook server.
Tests Vapi real-time tool calling, callback scheduling, end-of-call processing, and health checks.
"""

from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


def test_health_check():
    """Verifies that health check endpoint returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "whatsapp_provider" in data


def test_vapi_tool_call_midcall_whatsapp():
    """Verifies real-time tool-calls webhook execution for midcall WhatsApp."""
    payload = {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "test-call-123",
                "customer": {"number": "+918790513762"}
            },
            "toolCalls": [
                {
                    "id": "call_abc123",
                    "type": "function",
                    "function": {
                        "name": "trigger_midcall_whatsapp",
                        "arguments": {
                            "interest_summary": "15 kurtis collection with Razorpay",
                            "portfolio_category": "fashion"
                        }
                    }
                }
            ]
        }
    }

    response = client.post("/webhook/vapi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["toolCallId"] == "call_abc123"
    assert "sent the portfolio details" in data["results"][0]["result"]


def test_vapi_tool_call_schedule_callback():
    """Verifies real-time tool-calls webhook execution for callback scheduling."""
    payload = {
        "message": {
            "type": "tool-calls",
            "call": {
                "id": "test-call-456",
                "customer": {"number": "+918790513762"}
            },
            "toolCalls": [
                {
                    "id": "call_xyz789",
                    "type": "function",
                    "function": {
                        "name": "schedule_callback",
                        "arguments": {
                            "spoken_time_phrase": "tomorrow afternoon",
                            "topic": "Discuss MVP proposal with business partner",
                            "barrier_addressed": "Decision maker consultation"
                        }
                    }
                }
            ]
        }
    }

    response = client.post("/webhook/vapi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["toolCallId"] == "call_xyz789"
    assert "scheduled a callback" in data["results"][0]["result"].lower() or "callback" in data["results"][0]["result"].lower()


def test_vapi_end_of_call_report():
    """Verifies that end-of-call-report triggers post-call synthesis."""
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "id": "test-call-789",
                "customer": {"number": "+918790513762"}
            },
            "transcript": (
                "Assistant: Hey there! This is Ananya from ElevateBox.\n"
                "Lead: Hi, we make organic cosmetics, around 20 items.\n"
                "Assistant: Amazing! When do you plan to go live?\n"
                "Lead: In 2 weeks. Budget is 30k. Need Razorpay and courier shipping."
            )
        }
    }

    response = client.post("/webhook/vapi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["action"] == "post_call_dispatch_queued"
    assert data["turns"] == 4


def test_direct_endpoints():
    """Verifies direct HTTP trigger endpoints for mid-call WhatsApp and callbacks."""
    # 1. Direct mid-call WhatsApp
    res1 = client.post("/webhook/trigger-midcall-whatsapp", json={
        "phone_number": "+918790513762",
        "interest_summary": "Footwear store with COD"
    })
    assert res1.status_code == 200
    assert res1.json()["status"] == "success"

    # 2. Direct callback booking
    res2 = client.post("/webhook/schedule-callback", json={
        "spoken_time_phrase": "day after tomorrow at 4pm",
        "phone_number": "+918790513762",
        "topic": "Final contract review"
    })
    assert res2.status_code == 200
    assert res2.json()["status"] == "success"

    # 3. List callbacks
    res3 = client.get("/callbacks")
    assert res3.status_code == 200
    assert "callbacks" in res3.json()
    assert len(res3.json()["callbacks"]) >= 1


if __name__ == "__main__":
    print("Running server webhook integration tests...")
    test_health_check()
    test_vapi_tool_call_midcall_whatsapp()
    test_vapi_tool_call_schedule_callback()
    test_vapi_end_of_call_report()
    test_direct_endpoints()
    print("ALL SERVER WEBHOOK TESTS PASSED SUCCESSFULLY!")
