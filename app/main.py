import sys
import signal
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from app.database.connection import initialize_database
from app.ui.floating_widget import FloatingWidget
from app.services.prayer_service import PrayerCalculationService
from app.core.tracker import PrayerTracker
from app.notifications.notifier import DesktopNotifier
from app.database.repository import PrayerLogRepository
from app.ui.dashboard import DashboardWindow
from app.ui.tray import AppTrayIcon


def main():
    initialize_database()
    app = QApplication(sys.argv)
    
    repository = PrayerLogRepository()
    
    # Initialize Floating Widget and Dashboard
    widget = FloatingWidget()
    widget.show()

    prayer_service = None
    last_known_prayer = None
    notified_ending_for = None

    def update_logic():
        nonlocal last_known_prayer, notified_ending_for
        
        if not prayer_service:
            return

        now = datetime.now(prayer_service.tz)
        today = now.date()
        tomorrow = today + timedelta(days=1)

        today_times = prayer_service.get_prayer_times(today)
        tomorrow_times = prayer_service.get_prayer_times(tomorrow)

        current_p, next_p, countdown, progress, seconds_left = PrayerTracker.get_status(
            today_times, tomorrow_times, now
        )

        if dashboard.prayer_list_layout.count() == 0:
            dashboard.populate_prayers(today_times)

        widget.update_display(current_p, next_p, countdown, progress)

        if last_known_prayer is None:
            last_known_prayer = current_p
        elif current_p != last_known_prayer:
            DesktopNotifier.send(
                title="Time for Prayer",
                message=f"It is now time for {current_p} prayer.",
                icon_name="appointment-new"
            )
            last_known_prayer = current_p
            
        if seconds_left <= 600 and notified_ending_for != current_p:
            if current_p != "Sunrise": 
                DesktopNotifier.send(
                    title="Wakto Ending Soon!",
                    message=f"Only 10 minutes left for {current_p}! Next is {next_p}.",
                    icon_name="dialog-warning"
                )
            notified_ending_for = current_p

    def reload_settings():
        nonlocal prayer_service
        
        lat = float(repository.get_setting("latitude", "24.7471"))
        lon = float(repository.get_setting("longitude", "90.4203"))
        method = repository.get_setting("calc_method", "KARACHI")
        is_hanafi = repository.get_setting("is_hanafi", "True") == "True"
        
        prayer_service = PrayerCalculationService(
            latitude=lat, 
            longitude=lon, 
            method_name=method,
            is_hanafi_asr=is_hanafi
        )
        
        if 'dashboard' in locals():
            for i in reversed(range(dashboard.prayer_list_layout.count())): 
                w = dashboard.prayer_list_layout.itemAt(i).widget()
                if w: w.setParent(None)
                
        update_logic()

    dashboard = DashboardWindow(repository, on_settings_saved=reload_settings)
    # NOTE: dashboard.show() is removed from startup! It stays hidden.

    # Connect widget 3-dot menu button to open the dashboard window
    def open_dashboard():
        dashboard.show()
        dashboard.raise_()
        dashboard.activateWindow()

    widget.menu_clicked.connect(open_dashboard)

    reload_settings()

    app.setQuitOnLastWindowClosed(False)
    tray_icon = AppTrayIcon(dashboard, widget)
    tray_icon.show()

    timer = QTimer()
    timer.timeout.connect(update_logic)
    timer.start(1000)
    
    update_logic()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()