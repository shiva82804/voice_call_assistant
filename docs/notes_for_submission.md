# Voice Call Assistant - Engineering Notes

**Target Lead Call Verification**: +91 8790513762  

### 1. What Works
- **Autonomous Outbound Dialing**: Dials target lead automatically with room background noise and barge-in cut-off.
- **Trilingual Speech & Code-Switching**: Handles Telugu, Hindi, and English (plus Tenglish/Hinglish) without tripping or resetting context.
- **Organic 5-Dimension Discovery**: Dynamically captures products, SKU scale, features, timeline, and budget through active listening and piggybacking.
- **Intent-Driven Mid-Call WhatsApp**: Asynchronously fires portfolio/pricing WhatsApp alert mid-conversation when "HOT" intent is detected.
- **IST Callback Scheduler**: Accurately resolves colloquial speech (*"tomorrow morning"*, *"repu morning 11 ki"*, *"kal subah 10 baje"*) into scheduled datetime records.
- **Contextual Post-Call Synthesis**: WhatsApp message frames specific customer inputs, contact phone number, and architecture diagram.

### 2. What Does Not (Current Limitations)
- High telecommunication background noise on Indian mobile networks can occasionally cause phonetic STT drops on rapid regional slang.
- Multi-party conference bridging when a caller says "speak to my partner right now" is handled via callback rather than instant 3-way live transfer.

### 3. What I Would Build Next
- Integration with Exotel / Tata Telephony SIP trunks for Indian local CLI whitelisting.
- Streaming WebRTC client dashboard with live visual sentiment dials and human agent barge-in takeover.
