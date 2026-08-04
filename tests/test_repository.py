"""
Tests for repository settings + helper methods (get_record, save_record,
get_completed_count, get_setting, save_setting, get_monthly_data,
get_last_7_days_data).

The streak logic is tested separately in test_repository_streaks.py.
"""

from __future__ import annotations

import datetime as _dt

from app.core.models import PrayerRecord
from app.database.repository import PrayerLogRepository

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def test_get_setting_returns_default_when_missing(isolated_db):
    repo = PrayerLogRepository()
    assert repo.get_setting("nonexistent_key", "fallback") == "fallback"


def test_get_setting_returns_default_when_no_default(isolated_db):
    repo = PrayerLogRepository()
    assert repo.get_setting("nonexistent_key") is None


def test_save_and_get_setting_round_trips(isolated_db):
    repo = PrayerLogRepository()
    repo.save_setting("city", "Dhaka")
    assert repo.get_setting("city") == "Dhaka"


def test_save_setting_upserts(isolated_db):
    repo = PrayerLogRepository()
    repo.save_setting("city", "Dhaka")
    repo.save_setting("city", "London")
    assert repo.get_setting("city") == "London"


# ---------------------------------------------------------------------------
# Records: get_record, save_record, get_completed_count
# ---------------------------------------------------------------------------


def test_get_record_returns_none_when_absent(isolated_db):
    repo = PrayerLogRepository()
    assert repo.get_record("2026-01-15", "Fajr") is None


def test_save_then_get_record_round_trip(isolated_db):
    repo = PrayerLogRepository()
    repo.save_record(
        PrayerRecord(
            date="2026-01-15",
            prayer_name="Fajr",
            is_completed=True,
            completed_at=_dt.datetime(2026, 1, 15, 5, 30),
            is_jamaah=True,
        )
    )
    record = repo.get_record("2026-01-15", "Fajr")
    assert record is not None
    assert record.is_completed is True
    assert record.is_jamaah is True
    assert record.completed_at == _dt.datetime(2026, 1, 15, 5, 30)


def test_save_record_upserts(isolated_db):
    repo = PrayerLogRepository()
    repo.save_record(PrayerRecord(date="2026-01-15", prayer_name="Fajr", is_completed=True))
    repo.save_record(PrayerRecord(date="2026-01-15", prayer_name="Fajr", is_completed=False))
    record = repo.get_record("2026-01-15", "Fajr")
    assert record.is_completed is False


def test_get_completed_count_counts_only_completed(isolated_db):
    repo = PrayerLogRepository()
    target = "2026-01-15"
    # Three completed, one uncompleted, one in-progress (completed=False).
    for name in ("Fajr", "Dhuhr", "Asr"):
        repo.save_record(PrayerRecord(date=target, prayer_name=name, is_completed=True))
    repo.save_record(PrayerRecord(date=target, prayer_name="Maghrib", is_completed=False))
    repo.save_record(PrayerRecord(date=target, prayer_name="Isha", is_completed=False))
    assert repo.get_completed_count(target) == 3


def test_get_completed_count_empty(isolated_db):
    repo = PrayerLogRepository()
    assert repo.get_completed_count("2026-01-15") == 0


# ---------------------------------------------------------------------------
# Heatmap / weekly data
# ---------------------------------------------------------------------------


def test_get_monthly_data_returns_zero_for_missing_days(isolated_db):
    repo = PrayerLogRepository()
    # No records for this month; the method should return an empty dict, not
    # include zero entries for every day. Behavior here: returns {}.
    assert repo.get_monthly_data(2026, 1) == {}


def test_get_monthly_data_filters_by_month(isolated_db):
    repo = PrayerLogRepository()
    repo.save_record(PrayerRecord(date="2026-01-15", prayer_name="Fajr", is_completed=True))
    repo.save_record(PrayerRecord(date="2026-01-15", prayer_name="Dhuhr", is_completed=True))
    repo.save_record(PrayerRecord(date="2026-02-15", prayer_name="Fajr", is_completed=True))
    data = repo.get_monthly_data(2026, 1)
    assert data == {"2026-01-15": 2}


def test_get_last_7_days_data_includes_all_days(isolated_db):
    repo = PrayerLogRepository()
    data = repo.get_last_7_days_data()
    today = _dt.date.today()
    expected_dates = {(today - _dt.timedelta(days=i)).isoformat() for i in range(7)}
    assert set(data.keys()) == expected_dates
    # No records inserted; everything should be 0.
    assert all(v == 0 for v in data.values())


def test_get_last_7_days_data_aggregates_per_day(isolated_db):
    repo = PrayerLogRepository()
    today = _dt.date.today()
    today_str = today.isoformat()
    for name in ("Fajr", "Dhuhr", "Asr"):
        repo.save_record(PrayerRecord(date=today_str, prayer_name=name, is_completed=True))
    data = repo.get_last_7_days_data()
    assert data[today_str] == 3
