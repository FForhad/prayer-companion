from dataclasses import dataclass
from datetime import datetime


@dataclass
class DailyPrayerTimes:
    """
    Core domain model representing prayer times for a single day.
    Our application will use this instead of adhanpy's internal classes.
    """
    fajr: datetime
    sunrise: datetime
    dhuhr: datetime
    asr: datetime
    maghrib: datetime
    isha: datetime

from typing import Optional

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