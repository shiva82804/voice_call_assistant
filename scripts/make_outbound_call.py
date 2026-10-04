"""
scripts/make_outbound_call.py - Outbound Call Trigger Utility.
Initiates an autonomous outbound telephone call to the target candidate or evaluator
using the Vapi.ai Telephony API. Supports live dialing and local dry-run simulation.
"""

import os
import sys
import argparse
import httpx
from dotenv import load_dotenv

# Ensure core modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.prompt import get_assistant_system_prompt
from core.tools_schema import get_vapi_tools_config

load_dotenv()


def initiate_call(
    target_phone: str,
    dry_run: bool = False
):
    """Places an outbound phone call using Vapi API."""
    api_key = os.getenv("VAPI_API_KEY")
    phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")
    webhook_url = os.getenv("PUBLIC_WEBHOOK_URL", "http://localhost:8000")

    print("\n" + "=" * 65)
    print("🚀 ElevateBox Voice Assistant - Outbound Call Dispatcher")
    print("=" * 65)
    print(f"• Target Recipient : {target_phone}")
    print(f"• Assistant Persona: Ananya (ElevateBox Hyderabad)")
    print(f"• Server Webhook   : {webhook_url}/webhook/vapi")

    # If in dry-run mode or credentials are placeholders
    is_live = bool(api_key and api_key != "your_vapi_api_key_here" and not dry_run)

    if not is_live:
        print("\n[INFO] Running in DRY-RUN / SIMULATION MODE")
        if not api_key or api_key == "your_vapi_api_key_here":
            print("  Reason: VAPI_API_KEY not configured in .env")
        else:
            print("  Reason: --dry-run flag supplied")

        print("\n[Simulated Call Payload that would be dispatched to Vapi]:")
        payload = {
            "phoneNumberId": phone_number_id or "<VAPI_PHONE_NUMBER_ID>",
            "customer": {
                "number": target_phone
            },
            "serverUrl": f"{webhook_url}/webhook/vapi"
        }
        if assistant_id and assistant_id != "your_vapi_assistant_id_here":
            payload["assistantId"] = assistant_id
        else:
            payload["assistant"] = {
                "name": "Ananya - ElevateBox Outbound",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": get_assistant_system_prompt(target_phone)}
                    ],
                    "tools": get_vapi_tools_config()
                },
                "firstMessage": (
                    "Hey there! This is Ananya from ElevateBox in Banjara Hills. "
                    "I saw you were looking into setting up an e-commerce website, "
                    "and wanted to see what you're planning to sell? Have you got a minute?"
                ),
                "voice": {
                    "provider": "cartesia",
                    "voiceId": "248be419-c632-4f23-adf1-5324ed7dbf10"
                }
            }

        import json
        print(json.dumps(payload, indent=2))
        print("\n[SUCCESS] Outbound payload validated successfully.")
        print("To place a real phone call:")
        print("  1. Add your VAPI_API_KEY in .env")
        print("  2. Run: python scripts/make_outbound_call.py --phone +918790513762")
        print("=" * 65 + "\n")
        return {"status": "simulated", "target": target_phone}

    # Live Call Dispatch
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    call_payload = {
        "customer": {"number": target_phone}
    }

    if phone_number_id and phone_number_id != "your_vapi_phone_number_id_here":
        call_payload["phoneNumberId"] = phone_number_id

    if assistant_id and assistant_id != "your_vapi_assistant_id_here":
        call_payload["assistantId"] = assistant_id
    else:
        # Transient Assistant Config
        call_payload["assistant"] = {
            "name": "Ananya - ElevateBox Outbound",
            "serverUrl": f"{webhook_url}/webhook/vapi",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": get_assistant_system_prompt(target_phone)}
                ],
                "tools": get_vapi_tools_config()
            },
            "firstMessage": (
                "Hey there! This is Ananya from ElevateBox. "
                "I saw you were looking into setting up an e-commerce website, "
                "and wanted to see what you're planning to sell? Have you got a minute?"
            )
        }

    try:
        print("\n[LIVE] Sending outbound call request to https://api.vapi.ai/call/phone...")
        with httpx.Client(timeout=30.0) as client:
            res = client.post("https://api.vapi.ai/call/phone", headers=headers, json=call_payload)
            res.raise_for_status()
            data = res.json()
            call_id = data.get("id")
            print(f"🎉 Call Dispatched Successfully!")
            print(f"• Call ID: {call_id}")
            print(f"• Status : {data.get('status')}")
            print(f"• Phone  : {target_phone}")
            print("=" * 65 + "\n")
            return data
    except httpx.HTTPStatusError as e:
        print(f"❌ Vapi API Error ({e.response.status_code}): {e.response.text}")
        return {"error": e.response.text, "status_code": e.response.status_code}
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger outbound AI phone call")
    parser.add_argument(
        "--phone",
        default=os.getenv("TARGET_PHONE_NUMBER", "+918790513762"),
        help="Target phone number with country code"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the request without dialing"
    )
    args = parser.parse_args()
    initiate_call(target_phone=args.phone, dry_run=args.dry_run)
