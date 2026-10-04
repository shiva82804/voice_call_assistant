# AI Voice Calling Assistant

An autonomous, low-latency, trilingual outbound voice calling system. Built for real-world e-commerce sales qualification with organic conversational discovery, mid-call WhatsApp trigger dispatch, colloquial IST callback scheduling, and rich post-call follow-ups.

---

## 🌟 Key Architecture & Features

```
+----------------------------------------------------------------------------------------------------+
|                                     AI VOICE ASSISTANT PIPELINE                                    |
|                                                                                                    |
|  [ Target Phone ] <====== Telephony ======> [ Vapi Voice Gateway ]                                 |
|  (+91 8790513762)                            - Deepgram Nova-2 (STT)                               |
|                                              - Cartesia Indian Voice (TTS)                         |
|                                              - Barge-in & Office Room Ambience                     |
|                                                              |                                     |
|                                                       Real-time Audio / Tools                      |
|                                                              v                                     |
|                                                   [ GPT-4o Brain / Ananya ]                        |
|                                                    - <25 Words/turn Pacing                         |
|                                                    - Telugu, Hindi, English                        |
|                                                    - 5-Dimension Discovery                         |
|                                                              |                                     |
|                              +-------------------------------+-------------------------------+     |
|                              |                                                               |     |
|                              v (Mid-Call "HOT" Intent)                                       v     |
|                   [ Function: trigger_midcall_whatsapp ]                           [ Function: schedule_callback ]
|                              |                                                               |     |
|                              +-------------------------------+-------------------------------+     |
|                                                              |                                     |
|                                                              v                                     |
|                                            [ FastAPI Webhook Server (Port 8000) ]                  |
|                                                              |                                     |
|                              +-------------------------------+-------------------------------+     |
|                              |                                                               |     |
|                              v                                                               v     |
|                    [ WhatsApp Service ]                                            [ IST Callback Engine ] |
|                    - Meta Cloud / Twilio API                                       - Resolves "tomorrow morning"
|                    - Mid-call Portfolio Alert                                      - Telugu / Hindi expressions  
|                    - Architecture Diagram (PNG)                                    - JSON persistence            
+----------------------------------------------------------------------------------------------------+
```

1. **Autonomous Outbound Dialing**: Dials leads directly via Vapi / Twilio SIP trunks with low-latency streaming and office room noise.
2. **Trilingual Code-Switching**: Speaks English, Telugu, and Hindi seamlessly (including Tenglish and Hinglish) matching caller dialect instantly.
3. **Organic 5-Dimension Discovery**: Dynamically captures:
   - **Product Niche** (Fashion, Organic Food, Jewelry, Electronics, etc.)
   - **SKU Count** (Catalog size)
   - **Target Timeline** (Launch urgency)
   - **Budget Range** (Investment scope)
   - **Key Features** (Razorpay, COD, automated shipping, mobile design)
4. **Active Listening & Piggybacking**: When a caller provides multiple details at once, Ananya acknowledges them organically and advances to remaining questions without repetitive robotic interrogation.
5. **Real-Time Intent Execution (Mid-Call WhatsApp)**:
   - **HOT Leads**: Triggers immediate WhatsApp portfolio message mid-conversation while still on the call.
   - **WARM Leads**: Identifies barriers (budget constraints, decision maker, timing) and proposes staged MVP builds or callback schedules.
   - **COLD Leads**: Delivers a polite sign-off and offers a WhatsApp brochure.
6. **IST Spoken Callback Scheduler**: Converts natural expressions (*"tomorrow morning"*, *"repu morning 11 ki"*, *"kal subah 10 baje"*, *"in 2 hours"*) into exact Indian Standard Time (UTC+05:30) records with natural verbal confirmations.
7. **Post-Call Delivery**: Processes end-of-call transcripts and sends:
   - Human-framed contextual recap message
   - Contact phone number
   - System Architecture Diagram (`assets/architecture_diagram.png`)

---

## 📂 Project Structure

```
├── assets/
│   └── architecture_diagram.png    # Pre-rendered visual system architecture
├── core/
│   ├── classifier.py               # Multilingual intent classifier & 5-dimension parser
│   ├── prompt.py                   # Master system prompt for consultant persona "Ananya"
│   ├── scheduler.py                # Spoken natural language IST callback scheduler
│   ├── schemas.py                  # Pydantic data models & contracts
│   └── tools_schema.py             # Vapi/OpenAI function definitions
├── data/
│   └── test_callbacks.json         # Persisted callback bookings
├── docs/
│   └── notes_for_submission.md     # Architecture and engineering notes
├── scripts/
│   ├── generate_architecture_diagram.py  # Pillow generator for high-res architecture PNG
│   ├── make_outbound_call.py             # Script to trigger outbound call via Vapi API
│   └── setup_vapi_assistant.py           # Syncs prompt, tools, and voice settings to Vapi
├── services/
│   ├── post_call_processor.py      # Post-call transcript analysis & WhatsApp dispatch
│   └── whatsapp_service.py         # Multi-provider (Twilio, Meta, Mock) WhatsApp engine
├── tests/
│   ├── test_part1_intelligence.py  # Intent classification, prompt, & discovery unit tests
│   ├── test_part4_scheduler.py     # Colloquial IST scheduling unit tests
│   ├── test_part6_post_call.py     # Post-call synthesis unit tests
│   └── test_server_webhooks.py     # FastAPI webhook & tool calling integration tests
├── requirements.txt                # Python project dependencies
├── server.py                       # FastAPI real-time webhook server
└── README.md                       # Complete documentation
```

---

## 🚀 Quickstart Guide

### 1. Installation

Ensure Python 3.10+ is installed, then install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration

Create or configure your environment variables in `.env` (refer to conceptual parameters below):
- `TARGET_PHONE_NUMBER`: Recipient phone number (e.g. `+918790513762`).
- `WHATSAPP_PROVIDER`: Choose `mock` (for local simulation), `twilio`, or `meta`.
- `VAPI_API_KEY`: Your Vapi API Key.
- `PUBLIC_WEBHOOK_URL`: Your ngrok or deployed server URL (e.g. `https://xxxx.ngrok-free.app`).

### 3. Run Verification Tests

Run the test suite directly:
```bash
python tests/test_part1_intelligence.py
python tests/test_part4_scheduler.py
python tests/test_part6_post_call.py
python tests/test_server_webhooks.py
```
Or using pytest:
```bash
pytest tests/ -v
```

### 4. Start the Webhook Server

```bash
python server.py
# or using uvicorn directly:
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at `http://localhost:8000`. You can expose it via ngrok:
```bash
ngrok http 8000
```
Update `PUBLIC_WEBHOOK_URL` in `.env` with your ngrok URL.

### 5. Sync Assistant with Vapi

To provision or update the assistant on Vapi:
```bash
python scripts/setup_vapi_assistant.py
```

### 6. Place an Outbound Call

Test with dry-run / simulation mode:
```bash
python scripts/make_outbound_call.py --dry-run
```

To dial the live target number:
```bash
python scripts/make_outbound_call.py --phone +918790513762
```

---

## 📡 API Endpoints

- `GET /health`: Health check and status of assets and WhatsApp provider.
- `POST /webhook/vapi`: Unified endpoint for Vapi `tool-calls`, `function-call`, and `end-of-call-report`.
- `POST /webhook/trigger-midcall-whatsapp`: Directly dispatches mid-call WhatsApp message.
- `POST /webhook/schedule-callback`: Parses spoken time phrase and persists booking.
- `GET /callbacks`: Returns all scheduled callback records.
- `POST /webhook/post-call`: Processes transcript and dispatches follow-up recap message and architecture diagram.

---
