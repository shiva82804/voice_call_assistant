"""
services/whatsapp_service.py - Multi-provider WhatsApp messaging layer.
Supports Twilio WhatsApp, Meta WhatsApp Cloud API, and a robust Mock provider for local testing.
Handles text messages, image attachments (architecture diagram), and PDF documents (candidate resume).
"""

import os
import json
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class WhatsAppService:
    """Unified interface for dispatching WhatsApp messages and media."""

    def __init__(self):
        self.provider = os.getenv("WHATSAPP_PROVIDER", "mock").lower()
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
        self.meta_token = os.getenv("META_WHATSAPP_TOKEN")
        self.meta_phone_id = os.getenv("META_PHONE_NUMBER_ID")

    def send_text_message(self, recipient_phone: str, message_body: str) -> Dict[str, Any]:
        """Sends a plain text message to the recipient on WhatsApp."""
        if self.provider == "twilio" and self.twilio_sid and self.twilio_token:
            return self._send_twilio_message(recipient_phone, message_body)
        elif self.provider == "meta" and self.meta_token and self.meta_phone_id:
            return self._send_meta_message(recipient_phone, message_body)
        else:
            return self._send_mock_message(recipient_phone, message_body)

    def send_media_message(
        self,
        recipient_phone: str,
        caption: str,
        media_url_or_path: str,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """Sends an image or document attachment to the recipient on WhatsApp."""
        if self.provider == "twilio" and self.twilio_sid and self.twilio_token:
            return self._send_twilio_media(recipient_phone, caption, media_url_or_path)
        elif self.provider == "meta" and self.meta_token and self.meta_phone_id:
            return self._send_meta_media(recipient_phone, caption, media_url_or_path, media_type)
        else:
            return self._send_mock_media(recipient_phone, caption, media_url_or_path, media_type)

    # --------------------------------------------------------------------------
    # Mock Provider (Safe for local runs without external API credentials)
    # --------------------------------------------------------------------------
    def _send_mock_message(self, recipient: str, body: str) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print(f"[MOCK WHATSAPP DISPATCHED] -> {recipient}")
        print("-" * 60)
        # Safely print body handling console encoding limitations
        try:
            print(body)
        except UnicodeEncodeError:
            print(body.encode("ascii", errors="replace").decode("ascii"))
        print("=" * 60 + "\n")
        return {"status": "success", "provider": "mock", "recipient": recipient, "type": "text"}

    def _send_mock_media(self, recipient: str, caption: str, media_path: str, media_type: str) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print(f"[MOCK WHATSAPP MEDIA DISPATCHED] -> {recipient}")
        print(f"Type: {media_type.upper()} | Attachment: {media_path}")
        try:
            print(f"Caption:\n{caption}")
        except UnicodeEncodeError:
            print(f"Caption:\n{caption.encode('ascii', errors='replace').decode('ascii')}")
        print("=" * 60 + "\n")
        return {"status": "success", "provider": "mock", "recipient": recipient, "media": media_path}

    # --------------------------------------------------------------------------
    # Twilio WhatsApp Provider
    # --------------------------------------------------------------------------
    def _send_twilio_message(self, recipient: str, body: str) -> Dict[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        to_number = recipient if recipient.startswith("whatsapp:") else f"whatsapp:{recipient}"
        from_number = self.twilio_number if self.twilio_number.startswith("whatsapp:") else f"whatsapp:{self.twilio_number}"

        try:
            with httpx.Client() as client:
                res = client.post(
                    url,
                    auth=(self.twilio_sid, self.twilio_token),
                    data={"From": from_number, "To": to_number, "Body": body}
                )
                res.raise_for_status()
                return {"status": "success", "provider": "twilio", "response": res.json()}
        except Exception as e:
            print(f"Twilio WhatsApp dispatch error: {e}")
            return {"status": "error", "error": str(e)}

    def _send_twilio_media(self, recipient: str, caption: str, media_url: str) -> Dict[str, Any]:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
        to_number = recipient if recipient.startswith("whatsapp:") else f"whatsapp:{recipient}"
        from_number = self.twilio_number if self.twilio_number.startswith("whatsapp:") else f"whatsapp:{self.twilio_number}"

        try:
            with httpx.Client() as client:
                res = client.post(
                    url,
                    auth=(self.twilio_sid, self.twilio_token),
                    data={"From": from_number, "To": to_number, "Body": caption, "MediaUrl": media_url}
                )
                res.raise_for_status()
                return {"status": "success", "provider": "twilio", "response": res.json()}
        except Exception as e:
            print(f"Twilio WhatsApp Media error: {e}")
            return {"status": "error", "error": str(e)}

    # --------------------------------------------------------------------------
    # Meta WhatsApp Cloud API Provider
    # --------------------------------------------------------------------------
    def _send_meta_message(self, recipient: str, body: str) -> Dict[str, Any]:
        clean_phone = recipient.replace("+", "").replace(" ", "").replace("-", "")
        url = f"https://graph.facebook.com/v18.0/{self.meta_phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.meta_token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "text",
            "text": {"body": body}
        }
        try:
            with httpx.Client() as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                return {"status": "success", "provider": "meta", "response": res.json()}
        except Exception as e:
            print(f"Meta WhatsApp dispatch error: {e}")
            return {"status": "error", "error": str(e)}

    def _send_meta_media(self, recipient: str, caption: str, media_url: str, media_type: str) -> Dict[str, Any]:
        clean_phone = recipient.replace("+", "").replace(" ", "").replace("-", "")
        url = f"https://graph.facebook.com/v18.0/{self.meta_phone_id}/messages"
        headers = {"Authorization": f"Bearer {self.meta_token}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": media_type,
            media_type: {"link": media_url, "caption": caption}
        }
        try:
            with httpx.Client() as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                return {"status": "success", "provider": "meta", "response": res.json()}
        except Exception as e:
            print(f"Meta WhatsApp Media error: {e}")
            return {"status": "error", "error": str(e)}
