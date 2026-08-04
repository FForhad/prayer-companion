"""
Golden-vector tests for PrayerTracker.get_status.

The tracker is a pure function (no I/O, no clock reads, no Qt), so we
construct DailyPrayerTimes with concrete datetimes and pin the output.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

import pytest
from zoneinfo import ZoneInfo

from app.core.models import DailyPrayerTimes
from app.core.tracker import PrayerTracker


@pytest.fixture
def tz() -> ZoneInfo:
    return ZoneInfo("Asia/Dhaka")


def _build_day(tz, date_: datetime) -> DailyPrayerTimes:
    """Build a DailyPrayerTimes whose times are all on the given local date."""
    base = date_.astimezone(tz) if date_.tzinfo else date_.replace(tzinfo=tz)
    fajr = base.replace(hour=5, minute=0, second=0, microsecond=0)
    sunrise = base.replace(hour=6, minute=15, second=0, microsecond=0)
    dhuhr = base.replace(hour=12, minute=0, second=0, microsecond=0)
    asr = base.replace(hour=15, minute=30, second=0, microsecond=0)
    maghrib = base.replace(hour=18, minute=0, second=0, microsecond=0)
    isha = base.replace(hour=19, minute=30, second=0, microsecond=0)
    tomorrow_fajr = fajr + timedelta(days=1)
    night = tomorrow_fajr - maghrib
    return DailyPrayerTimes(
        fajr=fajr,
        sunrise=sunrise,
        dhuhr=dhuhr,
        asr=asr,
        maghrib=maghrib,
        isha=isha,
        tahajjud_start=tomorrow_fajr - night / 3,
    )


def _shift(day: DailyPrayerTimes, days: int = 1) -> DailyPrayerTimes:
    """Return a copy of `day` with every datetime shifted by `days`."""
    return replace(
        day,
        fajr=day.fajr + timedelta(days=days),
        sunrise=day.sunrise + timedelta(days=days),
        dhuhr=day.dhuhr + timedelta(days=days),
        asr=day.asr + timedelta(days=days),
        maghrib=day.maghrib + timedelta(days=days),
        isha=day.isha + timedelta(days=days),
        tahajjud_start=day.tahajjud_start + timedelta(days=days),
    )


# ---------------------------------------------------------------------------
# current_prayer / next_prayer mapping
# ---------------------------------------------------------------------------


def test_at_fajr_means_fajr_window(tz):
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    now = today.fajr  # the <= condition includes the boundary
    current, nxt, countdown, progress, secs = PrayerTracker.get_status(today, tomorrow, now)
    assert current == "Fajr"
    assert nxt == "Sunrise"
    # 75 minutes from 5:00 to 6:15 = 4500s
    assert 4500 - 2 <= secs <= 4500
    assert countdown.startswith("01:15:")  # 1h 15m until sunrise
    assert not countdown.startswith("-")


def test_between_maghrib_and_isha(tz):
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    now = datetime(2026, 1, 15, 18, 30, tzinfo=tz)  # 30 min after maghrib
    current, nxt, *_ = PrayerTracker.get_status(today, tomorrow, now)
    assert current == "Maghrib"
    assert nxt == "Isha"


def test_after_isha_until_tomorrow_fajr(tz):
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    now = datetime(2026, 1, 15, 23, 30, tzinfo=tz)
    current, nxt, _, _, secs = PrayerTracker.get_status(today, tomorrow, now)
    assert current == "Isha"
    assert nxt == "Fajr (Tomorrow)"
    # Until 5:00 next day = 5.5 hours = 19800 seconds
    assert 19800 - 2 <= secs <= 19800


def test_before_fajr_uses_default_label(tz):
    """
    Regression: when `now` is before today's Fajr, the for-else default keeps
    `current_prayer = "Isha (Yesterday)"`. This is the historical behavior and
    is pinned here so future changes are deliberate.
    """
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    now = datetime(2026, 1, 15, 3, 0, tzinfo=tz)
    current, nxt, *_ = PrayerTracker.get_status(today, tomorrow, now)
    assert current == "Isha (Yesterday)"
    assert nxt == "Fajr"


def test_countdown_format(tz):
    """HH:MM:SS shape, no leading minus, no negatives."""
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    now = datetime(2026, 1, 15, 10, 0, tzinfo=tz)
    _, _, countdown, *_ = PrayerTracker.get_status(today, tomorrow, now)
    assert not countdown.startswith("-")
    assert countdown.count(":") == 2
    hh, mm, ss = countdown.split(":")
    assert len(hh) == 2 and len(mm) == 2 and len(ss) == 2


def test_progress_at_midpoint_of_dhuhr_slot(tz):
    """Halfway between Dhuhr (12:00) and Asr (15:30) -> ~50%."""
    today = _build_day(tz, datetime(2026, 1, 15, 0, 0))
    tomorrow = _shift(today)
    # midpoint of 12:00–15:30 is 13:45
    now = datetime(2026, 1, 15, 13, 45, tzinfo=tz)
    _, _, _, progress, _ = PrayerTracker.get_status(today, tomorrow, now)
    # 105 min into a 210 min window = 50%
    assert 49 <= progress <= 51