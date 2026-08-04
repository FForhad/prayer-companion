"""
Streak semantics: get_current_streak and get_longest_streak.

Exercises the same logic we manually verified during the foundation pass,
but pinned as regression tests against an isolated SQLite DB.
"""
from __future__ import annotations

from datetime import date, timedelta

from app.core.models import PrayerRecord
from app.database.repository import PrayerLogRepository


ALL_FIVE = ("Fajr", "Dhuhr", "Asr", "Maghrib", "Isha")


def _fill_perfect(repo: PrayerLogRepository, day: date) -> None:
    """Mark all 5 prayers as completed for `day`."""
    for name in ALL_FIVE:
        repo.save_record(PrayerRecord(date=day.isoformat(), prayer_name=name, is_completed=True))


def _uncomplete_one(repo: PrayerLogRepository, day: date, prayer: str = "Isha") -> None:
    """Mark a single prayer as incomplete on `day` (without deleting the row)."""
    repo.save_record(PrayerRecord(date=day.isoformat(), prayer_name=prayer, is_completed=False))


def test_empty_db_returns_zero(isolated_db):
    repo = PrayerLogRepository()
    assert repo.get_current_streak() == 0
    assert repo.get_longest_streak() == 0


def test_single_perfect_today(isolated_db):
    repo = PrayerLogRepository()
    today = date.today()
    _fill_perfect(repo, today)
    assert repo.get_current_streak() == 1
    assert repo.get_longest_streak() == 1


def test_three_consecutive_perfect_days(isolated_db):
    repo = PrayerLogRepository()
    today = date.today()
    for offset in range(3):
        _fill_perfect(repo, today - timedelta(days=offset))
    assert repo.get_current_streak() == 3
    assert repo.get_longest_streak() == 3


def test_yesterday_broken_streak_anchors_on_today(isolated_db):
    repo = PrayerLogRepository()
    today = date.today()
    yesterday = today - timedelta(days=1)
    _fill_perfect(repo, today)
    _fill_perfect(repo, yesterday)
    _uncomplete_one(repo, yesterday, "Isha")
    assert repo.get_current_streak() == 1
    # Longest still considers all the historical 5/5 days. Today is the only perfect day.
    assert repo.get_longest_streak() == 1


def test_both_today_and_yesterday_imperfect_returns_zero(isolated_db):
    repo = PrayerLogRepository()
    today = date.today()
    yesterday = today - timedelta(days=1)
    _fill_perfect(repo, today)
    _uncomplete_one(repo, today, "Isha")
    _fill_perfect(repo, yesterday)
    _uncomplete_one(repo, yesterday, "Fajr")
    assert repo.get_current_streak() == 0


def test_gap_then_three_perfect_days(isolated_db):
    """
    Streaks must not bridge gaps. Three perfect days ending today, with a
    2-day gap before them, should still produce a 3-day current streak.
    """
    repo = PrayerLogRepository()
    today = date.today()
    # 2-day gap, then 3 perfect days ending today.
    for offset in range(3):
        _fill_perfect(repo, today - timedelta(days=offset))
    # Days today-3 and today-4 are deliberately empty.
    assert repo.get_current_streak() == 3
    assert repo.get_longest_streak() == 3


def test_longest_counts_disjoint_runs(isolated_db):
    """
    Longest streak should be the maximum over all disjoint runs of perfect days.
    """
    repo = PrayerLogRepository()
    today = date.today()
    # Run A: 2 perfect days today-20..today-21 (clearly separated from Run B)
    for offset in (20, 21):
        _fill_perfect(repo, today - timedelta(days=offset))
    # Run B: 4 perfect days today-3..today-6 (also clearly separated)
    for offset in range(3, 7):
        _fill_perfect(repo, today - timedelta(days=offset))
    # Run C: today's 5 prayers but with one missing -> not perfect
    for name in ALL_FIVE:
        repo.save_record(PrayerRecord(date=today.isoformat(), prayer_name=name, is_completed=True))
    _uncomplete_one(repo, today, "Fajr")

    assert repo.get_current_streak() == 0
    assert repo.get_longest_streak() == 4