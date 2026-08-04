"""
Application entry point.

Wiring only — all business logic lives in:
  - PrayerSessionState (controller): cached prayer times, day rollover, repaint tick.
  - PrayerScheduler: prayer-boundary + 10-min warning notifications (worker thread).
  - PrayerTracker: pure-function status calculations.
  - FloatingWidget / DashboardWindow: thin UI shells that subscribe to the controller.
"""
import sys

from PySide6.QtWidgets import QApplication

from app.core.session_state import PrayerSessionState
from app.core.tracker import PrayerTracker
from app.database.connection import initialize_database
from app.database.repository import PrayerLogRepository
from app.notifications.notifier import DesktopNotifier
from app.scheduler.prayer_scheduler import PrayerScheduler
from app.services.prayer_service import PrayerCalculationService
from app.ui.dashboard import DashboardWindow
from app.ui.floating_widget import FloatingWidget
from app.ui.tray import AppTrayIcon


def _build_service(repository: PrayerLogRepository) -> PrayerCalculationService:
    return PrayerCalculationService(
        latitude=float(repository.get_setting("latitude", "24.7471")),
        longitude=float(repository.get_setting("longitude", "90.4203")),
        method_name=repository.get_setting("calc_method", "KARACHI"),
        is_hanafi_asr=repository.get_setting("is_hanafi", "True") == "True",
    )


def main():
    initialize_database()
    app = QApplication(sys.argv)

    repository = PrayerLogRepository()

    # --- service + controller ---------------------------------------------
    service = _build_service(repository)
    session_state = PrayerSessionState(repository, service)
    scheduler = PrayerScheduler()

    # --- UI shells ---------------------------------------------------------
    widget = FloatingWidget()
    dashboard = DashboardWindow(repository, on_settings_saved=lambda: reload())

    # 1Hz repaint: re-query the tracker and update the floating widget.
    def repaint_widget() -> None:
        if session_state.today_times is None or session_state.tomorrow_times is None:
            return
        current, nxt, countdown, progress, _ = PrayerTracker.get_status(
            session_state.today_times,
            session_state.tomorrow_times,
            session_state.now,
        )
        widget.update_display(current, nxt, countdown, progress)

    session_state.tick.connect(repaint_widget)

    # Day rollover: rebuild the dashboard's checklist + progress.
    def on_day_rolled_over() -> None:
        if session_state.today_times is not None:
            dashboard.populate_prayers(session_state.today_times)
        dashboard.update_progress_ui()
        dashboard.update_statistics()

    session_state.day_rolled_over.connect(on_day_rolled_over)

    # --- notification callbacks (run in scheduler worker thread) ----------
    def on_boundary(current: str, nxt: str) -> None:
        # DesktopNotifier.send shells out to `notify-send`; no Qt dependency.
        DesktopNotifier.send(
            title="Time for Prayer",
            message=f"It is now time for {current} prayer.",
            icon_name="appointment-new",
        )

    def on_warn(current: str, nxt: str) -> None:
        if current == "Sunrise":
            return
        DesktopNotifier.send(
            title="Wakto Ending Soon!",
            message=f"Only 10 minutes left for {current}! Next is {nxt}.",
            icon_name="dialog-warning",
        )

    # --- settings reload --------------------------------------------------
    def reload() -> None:
        nonlocal service
        service = _build_service(repository)
        session_state.service = service  # setter recomputes and re-emits day_rolled_over if needed
        if session_state.today_times is not None and session_state.tomorrow_times is not None:
            scheduler.reschedule_all(
                session_state.today_times,
                session_state.tomorrow_times,
                on_boundary,
                on_warn,
            )

    # --- wire widget menu button + tray -----------------------------------
    widget.menu_clicked.connect(dashboard.show_then_raise)

    scheduler.start()
    reload()

    widget.show()
    tray_icon = AppTrayIcon(dashboard, widget)
    tray_icon.show()

    # Cleanup on quit.
    app.aboutToQuit.connect(scheduler.shutdown)
    app.aboutToQuit.connect(session_state.shutdown)
    app.setQuitOnLastWindowClosed(False)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()