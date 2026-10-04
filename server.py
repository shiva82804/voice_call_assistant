"""
server.py - FastAPI Webhook Server for Voice Call Assistant.
Handles real-time tool calls (mid-call WhatsApp, IST callback scheduling)
and post-call synthesis & document delivery from telephony engines (Vapi/Retell/Twilio).
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from core.schemas import (
    LeadDiscoveryData,
    MidCallWhatsAppPayload,
    CallbackSchedulePayload,
)
from core.scheduler import CallbackScheduler
from services.whatsapp_service import WhatsAppService
from services.post_call_processor import PostCallProcessor

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("voice_server")

# Instantiate core services
scheduler = CallbackScheduler(storage_path="data/test_callbacks.json")
whatsapp_service = WhatsAppService()
post_call_processor = PostCallProcessor(whatsapp_service=whatsapp_service)

TARGET_PHONE_NUMBER = os.getenv("TARGET_PHONE_NUMBER", "+918790513762")
CONSULTANT_NAME = os.getenv("CONSULTANT_NAME", "Ananya")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Voice Call Assistant Webhook Server starting up...")
    logger.info(f"Target phone configured: {TARGET_PHONE_NUMBER}")
    logger.info(f"WhatsApp provider active: {whatsapp_service.provider}")
    yield
    logger.info("Voice Call Assistant Webhook Server shutting down...")


app = FastAPI(
    title="Voice Call Assistant Webhook Server",
    description="Real-time function execution and post-call delivery pipeline for voice calls",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------------------
# 1. Health & Status
# ------------------------------------------------------------------------------
@app.get("/")
@app.get("/health")
async def health_check():
    """System health check and diagnostic endpoint."""
    return {
        "status": "healthy",
        "service": "Voice Call Assistant",
        "whatsapp_provider": whatsapp_service.provider,
        "target_phone": TARGET_PHONE_NUMBER,
        "assets_ready": {
            "diagram": os.path.exists("assets/architecture_diagram.png"),
        },
    }


# ------------------------------------------------------------------------------
# 2. Vapi Unified Webhook Endpoint
# ------------------------------------------------------------------------------
@app.post("/webhook/vapi")
async def handle_vapi_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Unified webhook handler for Vapi.
    Handles:
      - tool-calls / function-call: Real-time mid-call execution
      - end-of-call-report: Post-call transcript analysis and WhatsApp follow-up dispatch
      - status-update: Call state transitions
    """
    try:
        body = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    message = body.get("message", {})
    msg_type = message.get("type", "")
    logger.info(f"Received Vapi webhook message type: {msg_type}")

    # Extract customer phone if present
    call_obj = message.get("call", {})
    customer = call_obj.get("customer", {})
    customer_phone = customer.get("number") or call_obj.get("phoneNumber") or TARGET_PHONE_NUMBER

    # A. Real-Time Tool Calls (Modern Vapi format)
    if msg_type == "tool-calls":
        tool_calls = message.get("toolCalls", [])
        results = []
        for tool_call in tool_calls:
            tool_id = tool_call.get("id")
            func_obj = tool_call.get("function", {})
            func_name = func_obj.get("name")
            raw_args = func_obj.get("arguments", {})
            if isinstance(raw_args, str):
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {}
            else:
                args = raw_args

            result_str = execute_tool_call(func_name, args, customer_phone)
            results.append({"toolCallId": tool_id, "result": result_str})

        return JSONResponse(content={"results": results})

    # B. Legacy Function Call (Single function format)
    elif msg_type == "function-call":
        func_call = message.get("functionCall", {})
        func_name = func_call.get("name")
        raw_args = func_call.get("parameters", {})
        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args)
            except Exception:
                args = {}
        else:
            args = raw_args

        result_str = execute_tool_call(func_name, args, customer_phone)
        return JSONResponse(content={"result": result_str})

    # C. End-of-Call Report
    elif msg_type in ["end-of-call-report", "call-ended"]:
        logger.info(f"Processing end-of-call report for {customer_phone}...")
        transcript_lines = extract_transcript_lines(message)

        if transcript_lines:
            logger.info(f"Transcript contains {len(transcript_lines)} turns. Triggering post-call synthesis...")
            # Run post-call delivery in background
            background_tasks.add_task(
                post_call_processor.process_and_dispatch,
                conversation_transcript=transcript_lines,
                recipient_phone=customer_phone,
            )
            return {"status": "accepted", "action": "post_call_dispatch_queued", "turns": len(transcript_lines)}
        else:
            logger.warning("End-of-call report received with empty transcript.")
            return {"status": "ignored", "reason": "no_transcript"}

    # D. Status updates or other events
    return {"status": "acknowledged", "type": msg_type}


# ------------------------------------------------------------------------------
# 3. Tool Execution Dispatcher
# ------------------------------------------------------------------------------
def execute_tool_call(name: str, args: Dict[str, Any], caller_phone: str) -> str:
    """Dispatches tool calls from LLM and returns spoken/formatted result."""
    logger.info(f"Executing tool: {name} with args: {args}")

    if name == "trigger_midcall_whatsapp":
        recipient = args.get("phone_number") or caller_phone or TARGET_PHONE_NUMBER
        interest = args.get("interest_summary", "e-commerce website development")
        category = args.get("portfolio_category", "e-commerce")

        msg_body = (
            f"👋 Hi! This is Ananya following up mid-call.\n\n"
            f"Here is our quick portfolio & overview for your {interest} project:\n"
            f"• Tailored architecture & fast go-live\n"
            f"• Razorpay / COD integration & automated courier tracking\n"
            f"• High-converting mobile UI\n\n"
            f"Take a quick glance while we talk!"
        )

        whatsapp_service.send_text_message(recipient, msg_body)
        return (
            "I have just sent the portfolio details directly to your WhatsApp! "
            "You can open it and look through while we speak."
        )

    elif name == "schedule_callback":
        spoken_phrase = args.get("spoken_time_phrase", "tomorrow morning")
        topic = args.get("topic", "E-commerce website proposal discussion")
        barrier = args.get("barrier_addressed")
        recipient = args.get("phone_number") or caller_phone or TARGET_PHONE_NUMBER

        record = scheduler.book_callback(
            spoken_phrase=spoken_phrase,
            phone=recipient,
            topic=topic,
            barrier=barrier,
            language="en"
        )
        return record.verbal_confirmation

    else:
        logger.warning(f"Unrecognized tool call: {name}")
        return f"Tool {name} executed successfully."


def extract_transcript_lines(message: Dict[str, Any]) -> List[str]:
    """Extracts transcript lines from multiple possible Vapi report formats."""
    # 1. Direct transcript string
    if "transcript" in message and isinstance(message["transcript"], str) and message["transcript"].strip():
        # Split on newlines or assistant/user markers
        return [line.strip() for line in message["transcript"].split("\n") if line.strip()]

    # 2. Messages array in message or artifact
    messages_list = message.get("messages") or message.get("artifact", {}).get("messages") or []
    lines = []
    for m in messages_list:
        if isinstance(m, dict):
            role = m.get("role", "speaker").capitalize()
            content = m.get("message") or m.get("content") or ""
            if content:
                lines.append(f"{role}: {content}")

    return lines


# ------------------------------------------------------------------------------
# 4. Direct Functional Endpoints (For Testing & Manual Triggers)
# ------------------------------------------------------------------------------
class DirectMidCallRequest(BaseModel):
    phone_number: str = Field(default=TARGET_PHONE_NUMBER)
    interest_summary: str = Field(default="Organic oils e-commerce store with Razorpay")
    portfolio_category: Optional[str] = "Food & Organic"


@app.post("/webhook/trigger-midcall-whatsapp")
async def direct_midcall_whatsapp(payload: DirectMidCallRequest):
    """Manually test or trigger mid-call WhatsApp message."""
    res = execute_tool_call(
        "trigger_midcall_whatsapp",
        payload.model_dump(),
        caller_phone=payload.phone_number
    )
    return {"status": "success", "result": res}


class DirectCallbackRequest(BaseModel):
    spoken_time_phrase: str = Field(default="tomorrow morning")
    phone_number: str = Field(default=TARGET_PHONE_NUMBER)
    topic: str = Field(default="E-commerce proposal discussion")
    barrier: Optional[str] = None
    language: str = "en"


@app.post("/webhook/schedule-callback")
async def direct_schedule_callback(payload: DirectCallbackRequest):
    """Manually test or schedule an IST callback."""
    record = scheduler.book_callback(
        spoken_phrase=payload.spoken_time_phrase,
        phone=payload.phone_number,
        topic=payload.topic,
        barrier=payload.barrier,
        language=payload.language
    )
    return {"status": "success", "record": record}


@app.get("/callbacks")
async def list_callbacks():
    """Returns list of all booked callbacks."""
    return {"callbacks": scheduler.list_scheduled_callbacks()}


class DirectPostCallRequest(BaseModel):
    transcript: List[str]
    recipient_phone: str = Field(default=TARGET_PHONE_NUMBER)


@app.post("/webhook/post-call")
async def direct_post_call(payload: DirectPostCallRequest):
    """Manually trigger full post-call synthesis and WhatsApp follow-up dispatch."""
    result = post_call_processor.process_and_dispatch(
        conversation_transcript=payload.transcript,
        recipient_phone=payload.recipient_phone
    )
    return result


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    uvicorn.run("server:app", host=host, port=port, reload=True)
