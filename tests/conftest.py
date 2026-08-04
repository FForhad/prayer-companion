"""
Shared pytest fixtures.

The repository test fixtures point the DB at a private temp directory so we
never touch the user's real SQLite database.
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from zoneinfo import ZoneInfo

from app.core.models import DailyPrayerTimes
from app.database.connection import initialize_database


@pytest.fixture
def tz() -> ZoneInfo:
    return ZoneInfo("Asia/Dhaka")


def _dt(year: int, month: int, day: int, hour: int, minute: int, tz: ZoneInfo) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=tz)


@pytest.fixture
def make_day(tz):
    """
    Factory for DailyPrayerTimes with a sensible default spread of prayers.
    Tests can override individual times by keyword.
    """
    base_kwargs = dict(
        fajr=(5, 0),
        sunrise=(6, 15),
        dhuhr=(12, 0),
        asr=(15, 30),
        maghrib=(18, 0),
        isha=(19, 30),
    )

    def _factory(date_str: str = "2026-01-15", **overrides):
        year, month, day = (int(x) for x in date_str.split("-"))
        kwargs = {}
        for field, (h, m) in base_kwargs.items():
            kwargs[field] = _dt(year, month, day, h, m, tz)
            if field in overrides:
                kwargs[field] = overrides[field]
        # tahajjud_start is derived: 1/3 of the night ending at tomorrow's fajr.
        tomorrow_fajr = kwargs["fajr"] + timedelta(days=1)
        night = tomorrow_fajr - kwargs["maghrib"]
        kwargs["tahajjud_start"] = tomorrow_fajr - night / 3
        return DailyPrayerTimes(**kwargs)

    return _factory


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """
    Redirect the SQLite DB to a private directory and initialize the schema.
    Returns the path.
    """
    db_dir = tmp_path / ".local" / "share" / "prayer-companion"
    db_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.database.connection.DB_DIR", db_dir)
    monkeypatch.setattr("app.database.connection.DB_PATH", db_dir / "prayer_companion.db")
    initialize_database()
    return db_dir / "prayer_companion.db"