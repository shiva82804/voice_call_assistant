"""
tests/test_part4_scheduler.py - Verification suite for Sub-Part 4:
Natural Language Callback Scheduling from Spoken Speech (IST Timezone).
"""

import os
import shutil
from datetime import datetime, timedelta, timezone
from core.scheduler import CallbackScheduler, IST

TEST_STORAGE = "data/test_callbacks.json"


def setup_scheduler() -> CallbackScheduler:
    """Creates a scheduler pointing to an isolated test storage path."""
    if os.path.exists(TEST_STORAGE):
        os.remove(TEST_STORAGE)
    return CallbackScheduler(storage_path=TEST_STORAGE)


def test_tomorrow_morning_parsing():
    """Verifies 'tomorrow morning' parses to next day 10:00 AM IST."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 14, 0, 0, tzinfo=IST)  # Sunday 2 PM
    parsed = scheduler.parse_spoken_time("call me tomorrow morning", base_time=base_time)

    assert parsed.year == 2026
    assert parsed.month == 9
    assert parsed.day == 14  # Monday
    assert parsed.hour == 10
    assert parsed.minute == 0


def test_tomorrow_afternoon_and_evening():
    """Verifies afternoon and evening colloquial phrasing."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 11, 0, 0, tzinfo=IST)

    afternoon = scheduler.parse_spoken_time("tomorrow afternoon", base_time=base_time)
    assert afternoon.day == 14
    assert afternoon.hour == 14

    evening = scheduler.parse_spoken_time("tomorrow evening", base_time=base_time)
    assert evening.day == 14
    assert evening.hour == 18


def test_day_after_tomorrow_at_3pm():
    """Verifies 'day after tomorrow at 3pm' parses to +2 days, 15:00."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 10, 0, 0, tzinfo=IST)
    parsed = scheduler.parse_spoken_time("day after tomorrow at 3 pm", base_time=base_time)

    assert parsed.day == 15  # Tuesday
    assert parsed.hour == 15
    assert parsed.minute == 0


def test_telugu_spoken_time():
    """Verifies Telugu phrase 'repu morning 11 ki'."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 12, 0, 0, tzinfo=IST)
    parsed = scheduler.parse_spoken_time("repu morning 11 ki call cheyyandi", base_time=base_time)

    assert parsed.day == 14
    assert parsed.hour == 11


def test_hindi_spoken_time():
    """Verifies Hindi phrase 'kal subah 10 baje'."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 12, 0, 0, tzinfo=IST)
    parsed = scheduler.parse_spoken_time("kal subah 10 baje call karna", base_time=base_time)

    assert parsed.day == 14
    assert parsed.hour == 10


def test_relative_offset_in_hours():
    """Verifies 'in 2 hours'."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 14, 0, 0, tzinfo=IST)
    parsed = scheduler.parse_spoken_time("call me in 2 hours", base_time=base_time)

    assert parsed.hour == 16
    assert parsed.day == 13


def test_booking_persistence_and_verbal_confirmation():
    """Verifies full booking flow, confirmation text, and persistent storage."""
    scheduler = setup_scheduler()
    base_time = datetime(2026, 9, 13, 10, 0, 0, tzinfo=IST)

    record = scheduler.book_callback(
        spoken_phrase="call me back tomorrow morning",
        phone="+918790513762",
        topic="Discuss proposal with brother",
        barrier="Decision maker is brother",
        language="te",
        base_time=base_time
    )

    assert record.phone == "+918790513762"
    assert "repu morning" in record.verbal_confirmation.lower() or "callback" in record.verbal_confirmation.lower()
    assert record.status == "SCHEDULED"

    # Verify persisted in storage
    all_callbacks = scheduler.list_scheduled_callbacks()
    assert len(all_callbacks) == 1
    assert all_callbacks[0]["id"] == record.id
    assert all_callbacks[0]["phone"] == "+918790513762"


if __name__ == "__main__":
    print("Running scheduler tests directly...")
    test_tomorrow_morning_parsing()
    test_tomorrow_afternoon_and_evening()
    test_day_after_tomorrow_at_3pm()
    test_telugu_spoken_time()
    test_hindi_spoken_time()
    test_relative_offset_in_hours()
    test_booking_persistence_and_verbal_confirmation()
    print("ALL SCHEDULER TESTS PASSED SUCCESSFULLY!")
