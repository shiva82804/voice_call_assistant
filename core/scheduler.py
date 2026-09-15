"""
core/scheduler.py - Natural Language Callback Scheduler.
Parses colloquial and vague spoken time expressions (English, Telugu, Hindi)
into exact Indian Standard Time (IST, UTC+05:30) datetime records.
Fulfills ElevateBox Requirement 7 (10 points).
"""

import os
import re
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# Indian Standard Time (UTC+05:30)
IST = timezone(timedelta(hours=5, minutes=30))


class ScheduledCallbackRecord(BaseModel):
    """Data record representing a booked callback."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    phone: str
    spoken_phrase: str
    scheduled_time_iso: str
    scheduled_time_formatted: str
    verbal_confirmation: str
    topic: str = "E-commerce website proposal discussion"
    barrier: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(IST).isoformat())
    status: str = "SCHEDULED"


class CallbackScheduler:
    """Parses spoken time expressions and records bookings."""

    def __init__(self, storage_path: str = "data/scheduled_callbacks.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_current_ist_time(self) -> datetime:
        """Returns the current datetime in IST."""
        return datetime.now(IST)

    def parse_spoken_time(self, phrase: str, base_time: Optional[datetime] = None) -> datetime:
        """
        Parses vague or specific spoken expressions into an exact IST datetime.
        Supports:
          - 'tomorrow morning' -> Tomorrow 10:00 AM
          - 'tomorrow afternoon' -> Tomorrow 2:00 PM
          - 'tomorrow evening' -> Tomorrow 6:00 PM
          - 'day after tomorrow at 3pm'
          - 'next Monday at 4pm'
          - 'in 2 hours' / 'after 30 minutes'
          - Telugu: 'repu morning 11 ki', 'ellundu 3 ki'
          - Hindi: 'kal subah 10 baje', 'parso dopahar 3 baje'
        """
        now = base_time or self.get_current_ist_time()
        phrase_clean = phrase.lower().strip()

        target_date = now.date()
        target_hour = 10
        target_minute = 0

        # 1. Day offset detection
        if any(w in phrase_clean for w in ["day after tomorrow", "ellundu", "parso"]):
            target_date = now.date() + timedelta(days=2)
        elif any(w in phrase_clean for w in ["tomorrow", "repu", "kal"]):
            target_date = now.date() + timedelta(days=1)
        elif "today" in phrase_clean or "ee roju" in phrase_clean or "aaj" in phrase_clean:
            target_date = now.date()
        else:
            # Check for specific days of week (e.g. next monday, friday)
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for idx, day_name in enumerate(days):
                if day_name in phrase_clean:
                    current_day = now.weekday()
                    days_ahead = (idx - current_day) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    target_date = now.date() + timedelta(days=days_ahead)
                    break

        # 2. Relative time offset (e.g. "in 2 hours", "after 3 hours")
        hours_rel_match = re.search(r"(in|after)\s*(\d+)\s*hours?", phrase_clean)
        if hours_rel_match:
            hours_to_add = int(hours_rel_match.group(2))
            return now + timedelta(hours=hours_to_add)

        mins_rel_match = re.search(r"(in|after)\s*(\d+)\s*(mins?|minutes?)", phrase_clean)
        if mins_rel_match:
            mins_to_add = int(mins_rel_match.group(2))
            return now + timedelta(minutes=mins_to_add)

        # 3. Exact hour extraction (e.g. "at 3 pm", "11:30 am", "4 baje", "11 ki")
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm|ki|baje)?", phrase_clean)
        has_pm = "pm" in phrase_clean or "afternoon" in phrase_clean or "evening" in phrase_clean or "night" in phrase_clean or "dopahar" in phrase_clean or "shaam" in phrase_clean
        has_morning = "morning" in phrase_clean or "subah" in phrase_clean or "am" in phrase_clean

        # Extract explicit hour if present
        explicit_hour_found = False
        if time_match:
            num = int(time_match.group(1))
            # Only treat as hour if reasonable hour (1-12)
            if 1 <= num <= 12:
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                if "pm" in phrase_clean:
                    target_hour = num if num == 12 else num + 12
                elif "am" in phrase_clean:
                    target_hour = 0 if num == 12 else num
                elif has_pm and num < 12:
                    target_hour = num + 12
                else:
                    target_hour = num
                target_minute = minute
                explicit_hour_found = True

        # If no explicit hour was given, use colloquial defaults
        if not explicit_hour_found:
            if has_morning:
                target_hour = 10
                target_minute = 0
            elif "afternoon" in phrase_clean or "dopahar" in phrase_clean:
                target_hour = 14
                target_minute = 0
            elif "evening" in phrase_clean or "shaam" in phrase_clean:
                target_hour = 18
                target_minute = 0
            elif "night" in phrase_clean or "raat" in phrase_clean:
                target_hour = 20
                target_minute = 0
            else:
                # Default to tomorrow 10:00 AM if vague
                if target_date == now.date():
                    target_date = now.date() + timedelta(days=1)
                target_hour = 10
                target_minute = 0

        parsed_dt = datetime(
            year=target_date.year,
            month=target_date.month,
            day=target_date.day,
            hour=target_hour,
            minute=target_minute,
            tzinfo=IST
        )
        return parsed_dt

    def generate_verbal_confirmation(self, dt: datetime, language: str = "en") -> str:
        """Generates natural spoken confirmation in English, Telugu, or Hindi."""
        time_str = dt.strftime("%I:%M %p")
        day_str = dt.strftime("%A, %d %B")

        if language == "te":
            return f"Perfect andi, nenu callback ni {day_str} {time_str} IST ki schedule chesanu. Ma team nunchi call vastundi."
        elif language == "hi":
            return f"Theek hai, maine aapka callback {day_str} ko {time_str} IST par schedule kar diya hai. Hum call karenge."
        else:
            return f"Got it! I have scheduled a callback for you on {day_str} at {time_str} IST."

    def book_callback(
        self,
        spoken_phrase: str,
        phone: str = "+918790513762",
        topic: str = "E-commerce website proposal discussion",
        barrier: Optional[str] = None,
        language: str = "en",
        base_time: Optional[datetime] = None
    ) -> ScheduledCallbackRecord:
        """Parses the spoken phrase, generates confirmation, and records the booking."""
        scheduled_dt = self.parse_spoken_time(spoken_phrase, base_time=base_time)
        verbal_text = self.generate_verbal_confirmation(scheduled_dt, language=language)

        record = ScheduledCallbackRecord(
            phone=phone,
            spoken_phrase=spoken_phrase,
            scheduled_time_iso=scheduled_dt.isoformat(),
            scheduled_time_formatted=scheduled_dt.strftime("%A, %b %d %Y at %I:%M %p IST"),
            verbal_confirmation=verbal_text,
            topic=topic,
            barrier=barrier
        )

        # Persist booking
        self._save_record(record)
        return record

    def _save_record(self, record: ScheduledCallbackRecord):
        """Appends record to local JSON storage."""
        try:
            records = []
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    records = json.load(f)
            records.append(record.model_dump())
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
        except Exception as e:
            print(f"Warning: could not persist callback record: {e}")

    def list_scheduled_callbacks(self) -> List[Dict[str, Any]]:
        """Returns all scheduled callbacks."""
        if not os.path.exists(self.storage_path):
            return []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)
