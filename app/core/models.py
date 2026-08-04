from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class DailyPrayerTimes:
    """
    Core domain model representing prayer times for a single day.

    `tahajjud_start` is the start of the last third of the night (between today's
    Maghrib and tomorrow's Fajr), included so callers don't have to recompute it.
    """
    fajr: datetime
    sunrise: datetime
    dhuhr: datetime
    asr: datetime
    maghrib: datetime
    isha: datetime
    tahajjud_start: datetime


@dataclass
class PrayerRecord:
    """
    Represents a single prayer log entry in the database.
    """
    date: str              # Format: YYYY-MM-DD
    prayer_name: str       # Fajr, Dhuhr, Asr, Maghrib, Isha
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    is_jamaah: bool = False
    is_late: bool = False
    notes: Optional[str] = None
