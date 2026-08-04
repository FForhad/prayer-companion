"""
Session state controller.

Owns the cached today/tomorrow prayer times, detects day rollover, and emits
the Qt signals the UI subscribes to. A 1Hz QTimer is owned here purely for
repaint cadence; notification logic lives in PrayerScheduler, not here.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

from app.core.models import DailyPrayerTimes
from app.database.repository import PrayerLogRepository
from app.services.prayer_service import PrayerCalculationService


class PrayerSessionState(QObject):
    # (current, next) — fires when the active prayer changes.
    current_prayer_changed = Signal(str, str)
    # (current, next) — fires ~10 min before a non-Sunrise prayer ends.
    wakto_ending_soon = Signal(str, str)
    # Local date changed (midnight rollover).
    day_rolled_over = Signal()
    # 1Hz repaint tick. Cheap; just tells subscribers to refresh the countdown label.
    tick = Signal()

    def __init__(
        self,
        repository: PrayerLogRepository,
        service: PrayerCalculationService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self._repository = repository
        self._service = service
        self._today_date: Optional[date] = None
        self._today_times: Optional[DailyPrayerTimes] = None
        self._tomorrow_times: Optional[DailyPrayerTimes] = None
        # Suppress signals during initial setup.
        self._suppress_signals = False

        # Repaint cadence. Owned here so main.py doesn't have to manage a free-floating
        # QTimer. The scheduler handles notification jobs; this only paints.
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setInterval(1000)
        self._repaint_timer.timeout.connect(self._on_tick)
        self._repaint_timer.start()

    # --- service swap (settings change) -------------------------------------
    @property
    def service(self) -> PrayerCalculationService:
        return self._service

    @service.setter
    def service(self, service: PrayerCalculationService) -> None:
        self._service = service
        self._today_times = None
        self._tomorrow_times = None
        # Force recompute on next tick; today_date stays so rollover is still detected.
        self.recompute()

    # --- public API ---------------------------------------------------------
    def recompute(self) -> None:
        """Refresh today/tomorrow times. Emits day_rolled_over if date changed."""
        if not self._suppress_signals:
            now = datetime.now(self._service.tz)
            today = now.date()
            if self._today_date != today:
                self._service.clear_cache()
                self._today_date = today
                self.day_rolled_over.emit()

            self._today_times = self._service.get_prayer_times(today)
            self._tomorrow_times = self._service.get_prayer_times(today + timedelta(days=1))

    # --- read-only views ----------------------------------------------------
    @property
    def today_times(self) -> Optional[DailyPrayerTimes]:
        return self._today_times

    @property
    def tomorrow_times(self) -> Optional[DailyPrayerTimes]:
        return self._tomorrow_times

    @property
    def today_date(self) -> Optional[date]:
        return self._today_date

    @property
    def now(self) -> datetime:
        """Current wall clock in the service's timezone (or system tz if unset)."""
        return datetime.now(self._service.tz)

    # --- internals ----------------------------------------------------------
    def _on_tick(self) -> None:
        """1Hz slot. Cheap: detects date drift and emits tick for repaint."""
        if self._suppress_signals:
            return
        now = datetime.now(self._service.tz)
        today = now.date()
        if self._today_date != today:
            # Date drifted under us (e.g. system suspend). Don't emit day_rolled_over
            # directly; defer to recompute so callers can still receive the full update.
            self.recompute()
        self.tick.emit()

    def shutdown(self) -> None:
        """Stop the repaint timer. Called from app.aboutToQuit."""
        self._repaint_timer.stop()
