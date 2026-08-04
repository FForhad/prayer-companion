"""
Prayer-time notification scheduler.

Wraps apscheduler.schedulers.background.BackgroundScheduler. Jobs fire callbacks
in a worker thread; callbacks may use Qt signal emission (queued across threads
is automatic) to update the UI.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger

from app.core.models import DailyPrayerTimes

logger = logging.getLogger(__name__)

# Sunrise never gets a "wakto ending soon" warning.
PRAYERS_NO_WARN = {"Sunrise"}


def _make_timeline(
    today: DailyPrayerTimes, tomorrow: DailyPrayerTimes
) -> list[tuple[str, datetime]]:
    """
    Returns [(label, fire_at)] for: today's 5 prayers + Sunrise,
    plus tomorrow's Fajr. Order matches PrayerTracker.get_status's timeline.
    """
    return [
        ("Fajr", today.fajr),
        ("Sunrise", today.sunrise),
        ("Dhuhr", today.dhuhr),
        ("Asr", today.asr),
        ("Maghrib", today.maghrib),
        ("Isha", today.isha),
        ("Fajr (Tomorrow)", tomorrow.fajr),
    ]


class PrayerScheduler:
    """
    Owns the BackgroundScheduler lifecycle and reschedules jobs whenever the
    prayer times change (settings change or day rollover).
    """

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler(daemon=True)
        self._jobs: dict[str, str] = {}  # job_id -> apscheduler job id
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._scheduler.start()
        self._started = True

    def shutdown(self) -> None:
        """Called from app.aboutToQuit."""
        if not self._started:
            return
        try:
            self._scheduler.shutdown(wait=False)
        except Exception:  # pragma: no cover — defensive
            logger.exception("scheduler shutdown failed")
        self._started = False

    def reschedule_all(
        self,
        today: DailyPrayerTimes,
        tomorrow: DailyPrayerTimes,
        on_boundary: Callable[[str, str], None],
        on_warn: Callable[[str, str], None],
    ) -> None:
        """
        Cancel every previously-scheduled job and create fresh ones for the
        current today/tomorrow. Jobs whose fire time is already in the past
        are skipped.
        """
        self._cancel_all()

        timeline = _make_timeline(today, tomorrow)
        # Prayer-boundary pair: (current, next).
        for i in range(len(timeline) - 1):
            current_label, fire_at = timeline[i]
            next_label, _ = timeline[i + 1]
            if fire_at <= datetime.now(today.fajr.tzinfo):
                continue
            self._add_boundary_job(current_label, next_label, fire_at, on_boundary)
            if current_label not in PRAYERS_NO_WARN:
                warn_at = fire_at - timedelta(minutes=10)
                if warn_at > datetime.now(today.fajr.tzinfo):
                    self._add_warn_job(current_label, next_label, warn_at, on_warn)

    def pending_job_count(self) -> int:
        return len(self._jobs)

    # --- internals ----------------------------------------------------------
    def _add_boundary_job(
        self,
        current: str,
        nxt: str,
        fire_at: datetime,
        callback: Callable[[str, str], None],
    ) -> None:
        job_id = f"boundary:{current}@{fire_at.isoformat()}"
        self._scheduler.add_job(
            callback,
            trigger=DateTrigger(run_date=fire_at, timezone=fire_at.tzinfo),
            args=[current, nxt],
            id=job_id,
            misfire_grace_time=60,
            coalesce=True,
        )
        self._jobs[job_id] = job_id

    def _add_warn_job(
        self,
        current: str,
        nxt: str,
        fire_at: datetime,
        callback: Callable[[str, str], None],
    ) -> None:
        job_id = f"warn:{current}@{fire_at.isoformat()}"
        self._scheduler.add_job(
            callback,
            trigger=DateTrigger(run_date=fire_at, timezone=fire_at.tzinfo),
            args=[current, nxt],
            id=job_id,
            misfire_grace_time=60,
            coalesce=True,
        )
        self._jobs[job_id] = job_id

    def _cancel_all(self) -> None:
        for job_id in list(self._jobs.keys()):
            try:
                self._scheduler.remove_job(job_id)
            except Exception:  # pragma: no cover — job may have already fired
                pass
        self._jobs.clear()
