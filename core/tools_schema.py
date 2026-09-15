"""
core/tools_schema.py - Function calling tool definitions for Vapi, Retell, and OpenAI.
Used to trigger mid-call actions and book callbacks during live phone conversations.
"""

from typing import List, Dict, Any

TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "trigger_midcall_whatsapp",
            "description": (
                "Sends a WhatsApp message with portfolio and pricing details to the customer "
                "DURING the active phone call. MUST be called immediately when the customer displays "
                "high buying intent (HOT lead), such as asking for price, timeline, how soon we can start, "
                "or asking to see portfolio/samples right now."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Customer phone number in international E.164 format, e.g. +918790513762"
                    },
                    "interest_summary": {
                        "type": "string",
                        "description": "Brief summary of what customer wants to build (e.g. 20-product organic oil website with Razorpay)"
                    },
                    "portfolio_category": {
                        "type": "string",
                        "description": "Product niche category (e.g. fashion, food, jewelry, general e-commerce)"
                    }
                },
                "required": ["interest_summary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_callback",
            "description": (
                "Schedules a phone callback when the lead names a time or requires a follow-up "
                "(e.g. 'call me tomorrow morning', 'Friday at 3pm', 'my brother handles this, call back Monday')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "spoken_time_phrase": {
                        "type": "string",
                        "description": "The exact time phrase spoken by the caller, e.g. 'tomorrow morning', 'day after tomorrow at 4pm'"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Reason for callback (e.g. discuss proposal with partner, budget review)"
                    },
                    "barrier_addressed": {
                        "type": "string",
                        "description": "Identified hesitation or barrier, if any (e.g. budget, decision maker)"
                    }
                },
                "required": ["spoken_time_phrase"]
            }
        }
    }
]


def get_vapi_tools_config() -> List[Dict[str, Any]]:
    """Returns tools configured in Vapi tool format."""
    return TOOLS_SCHEMA


def get_openai_tools_config() -> List[Dict[str, Any]]:
    """Returns standard OpenAI tools format."""
    return TOOLS_SCHEMA
