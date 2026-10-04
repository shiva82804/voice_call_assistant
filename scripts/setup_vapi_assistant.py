"""
scripts/setup_vapi_assistant.py - Synchronizes Assistant Configuration with Vapi.
Uploads the engineered system prompt, voice parameters, ambient noise,
and real-time tool definitions to Vapi via REST API.
"""

import os
import sys
import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.prompt import get_assistant_system_prompt
from core.tools_schema import get_vapi_tools_config

load_dotenv()


def setup_assistant():
    """Creates or updates assistant on Vapi."""
    api_key = os.getenv("VAPI_API_KEY")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID")
    webhook_url = os.getenv("PUBLIC_WEBHOOK_URL", "http://localhost:8000")
    target_phone = os.getenv("TARGET_PHONE_NUMBER", "+918790513762")

    print("\n" + "=" * 65)
    print("⚙️  ElevateBox Voice Assistant - Vapi Assistant Provisioner")
    print("=" * 65)

    assistant_config = {
        "name": "Ananya - ElevateBox Outbound Consultant",
        "serverUrl": f"{webhook_url}/webhook/vapi",
        "model": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": get_assistant_system_prompt(target_phone)}
            ],
            "tools": get_vapi_tools_config()
        },
        "voice": {
            "provider": "cartesia",
            "voiceId": "248be419-c632-4f23-adf1-5324ed7dbf10",  # Natural conversational tone
            "fillerInjectionEnabled": True
        },
        "firstMessage": (
            "Hey there! This is Ananya from ElevateBox. "
            "I saw you were looking into setting up an e-commerce website, "
            "and wanted to see what you're planning to sell? Have you got a minute?"
        ),
        "endCallMessage": "Thanks so much for your time! I've sent all the details over WhatsApp. Have a great day!",
        "backgroundSound": "office",  # Ambient office background noise for natural realism
        "silenceTimeoutSeconds": 25,
        "maxDurationSeconds": 600,
        "responseDelaySeconds": 0.4
    }

    if not api_key or api_key == "your_vapi_api_key_here":
        print("\n[NOTE] VAPI_API_KEY is not configured in .env.")
        print("Generated Assistant Configuration JSON (ready to paste or sync):")
        import json
        print(json.dumps(assistant_config, indent=2))
        print("=" * 65 + "\n")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            if assistant_id and assistant_id != "your_vapi_assistant_id_here":
                # Update existing assistant
                print(f"Updating existing Vapi assistant ({assistant_id})...")
                res = client.patch(
                    f"https://api.vapi.ai/assistant/{assistant_id}",
                    headers=headers,
                    json=assistant_config
                )
            else:
                # Create new assistant
                print("Creating new Vapi assistant...")
                res = client.post(
                    "https://api.vapi.ai/assistant",
                    headers=headers,
                    json=assistant_config
                )

            res.raise_for_status()
            data = res.json()
            created_id = data.get("id")
            print(f"✅ Assistant configured successfully! Assistant ID: {created_id}")
            print(f"👉 Make sure to add this ID to your .env file: VAPI_ASSISTANT_ID={created_id}")
            print("=" * 65 + "\n")
            return data
    except Exception as e:
        print(f"❌ Failed to sync assistant with Vapi: {e}")


if __name__ == "__main__":
    setup_assistant()
