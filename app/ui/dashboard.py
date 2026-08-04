from datetime import datetime

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.models import DailyPrayerTimes, PrayerRecord
from app.database.repository import PrayerLogRepository
from app.ui.settings_window import SettingsWindow
from app.widgets.heatmap import MonthlyHeatmapWidget


class DashboardWindow(QWidget):
    def __init__(self, repository: PrayerLogRepository, on_settings_saved=None):
        super().__init__()
        self.repository = repository
        self.on_settings_saved = on_settings_saved

        self.setWindowTitle("Prayer Companion")
        # Resizable: minimum keeps the layout sensible on tiny windows.
        self.setMinimumSize(420, 600)
        self.resize(420, 640)

        self.setStyleSheet("""
            QWidget {
                background-color: #0b0f19;
                color: #f1f5f9;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            QTabWidget::pane {
                border: none;
                background-color: #0b0f19;
            }
            QTabBar::tab {
                background-color: #131b2e;
                color: #94a3b8;
                padding: 10px 18px;
                font-weight: 600;
                font-size: 13px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #1e293b;
                color: #ffffff;
                border-bottom: 2px solid #0284c7;
            }
            QTabBar::tab:hover {
                color: #ffffff;
            }
            QFrame#Card {
                background-color: #131b2e;
                border: 1px solid #1e293b;
                border-radius: 10px;
            }
            QCheckBox {
                font-size: 14px;
                font-weight: 600;
                spacing: 10px;
                color: #f8fafc;
            }
            QCheckBox::indicator {
                width: 18px; height: 18px; border-radius: 5px;
                border: 2px solid #475569; background-color: #0b0f19;
            }
            QCheckBox::indicator:hover { border-color: #38bdf8; }
            QCheckBox::indicator:checked { background-color: #10b981; border: 2px solid #10b981; }
            QProgressBar {
                background-color: #0b0f19; border: 1px solid #1e293b;
                border-radius: 4px; height: 6px; text-align: center; color: transparent;
            }
            QProgressBar::chunk { background-color: #10b981; border-radius: 3px; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()

        self.tab_today = QWidget()
        self.tab_analytics = QWidget()
        self.tab_settings = QWidget()

        self.init_today_tab()
        self.init_analytics_tab()
        self.init_settings_tab()

        self.tabs.addTab(self.tab_today, "📅 Today")
        self.tabs.addTab(self.tab_analytics, "📊 Analytics")
        self.tabs.addTab(self.tab_settings, "⚙ Settings")

        main_layout.addWidget(self.tabs)

        self.update_progress_ui()
        self.update_statistics()

    def init_today_tab(self):
        layout = QVBoxLayout(self.tab_today)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top Bar
        top_bar = QHBoxLayout()
        header_vbox = QVBoxLayout()
        header_vbox.setSpacing(1)

        self.lbl_header = QLabel("Daily Prayers")
        self.lbl_header.setStyleSheet("font-size: 18px; font-weight: 700; color: #ffffff;")
        self.lbl_date = QLabel(datetime.now().strftime("%a, %d %b"))
        self.lbl_date.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")

        header_vbox.addWidget(self.lbl_header)
        header_vbox.addWidget(self.lbl_date)
        top_bar.addLayout(header_vbox)
        top_bar.addStretch()

        self.lbl_streak = QLabel("🔥 0d Streak")
        self.lbl_streak.setStyleSheet("""
            background-color: #131b2e; color: #f59e0b; font-size: 11px;
            font-weight: 700; padding: 4px 8px; border-radius: 6px; border: 1px solid #1e293b;
        """)
        top_bar.addWidget(self.lbl_streak)
        layout.addLayout(top_bar)

        # Card: Checklist
        card_checklist = QFrame()
        card_checklist.setObjectName("Card")
        cl_layout = QVBoxLayout(card_checklist)
        cl_layout.setContentsMargins(12, 10, 12, 10)
        cl_layout.setSpacing(6)

        prog_row = QHBoxLayout()
        self.lbl_progress_text = QLabel("Today: 0/5 Completed")
        self.lbl_progress_text.setStyleSheet("font-size: 11px; font-weight: 600; color: #10b981;")
        prog_row.addWidget(self.lbl_progress_text)
        prog_row.addStretch()
        cl_layout.addLayout(prog_row)

        self.daily_progress = QProgressBar()
        self.daily_progress.setMaximum(5)
        cl_layout.addWidget(self.daily_progress)

        self.prayer_list_layout = QVBoxLayout()
        self.prayer_list_layout.setSpacing(2)
        cl_layout.addLayout(self.prayer_list_layout)

        layout.addWidget(card_checklist)

        # Card: Special & Reference Times (Sunrise & Tahajjud)
        card_special = QFrame()
        card_special.setObjectName("Card")
        sp_layout = QVBoxLayout(card_special)
        sp_layout.setContentsMargins(12, 8, 12, 8)
        sp_layout.setSpacing(4)

        lbl_sp_title = QLabel("Special & Reference Times")
        lbl_sp_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b;")
        sp_layout.addWidget(lbl_sp_title)

        # Sunrise Row
        sr_row = QHBoxLayout()
        sr_label = QLabel("🌅 Sunrise (Fajr Ends)")
        sr_label.setStyleSheet("font-size: 12px; color: #cbd5e1; font-weight: 500;")
        self.lbl_sunrise_val = QLabel("--:--")
        self.lbl_sunrise_val.setStyleSheet("font-size: 12px; color: #38bdf8; font-weight: 600;")
        sr_row.addWidget(sr_label)
        sr_row.addStretch()
        sr_row.addWidget(self.lbl_sunrise_val)
        sp_layout.addLayout(sr_row)

        # Tahajjud Row
        th_row = QHBoxLayout()
        th_label = QLabel("🌙 Tahajjud (Last ⅓ Night)")
        th_label.setStyleSheet("font-size: 12px; color: #cbd5e1; font-weight: 500;")
        self.lbl_tahajjud_val = QLabel("--:--")
        self.lbl_tahajjud_val.setStyleSheet("font-size: 12px; color: #a78bfa; font-weight: 600;")
        th_row.addWidget(th_label)
        th_row.addStretch()
        th_row.addWidget(self.lbl_tahajjud_val)
        sp_layout.addLayout(th_row)

        layout.addWidget(card_special)

        # Card: Heatmap
        card_stats = QFrame()
        card_stats.setObjectName("Card")
        st_layout = QVBoxLayout(card_stats)
        st_layout.setContentsMargins(12, 8, 12, 8)
        st_layout.setSpacing(4)

        lbl_hm_title = QLabel("Activity Overview")
        lbl_hm_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b;")
        st_layout.addWidget(lbl_hm_title)

        self.heatmap = MonthlyHeatmapWidget()
        st_layout.addWidget(self.heatmap)

        layout.addWidget(card_stats)

    def init_analytics_tab(self):
        layout = QVBoxLayout(self.tab_analytics)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(10)

        lbl_title = QLabel("Weekly Completion Performance")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        layout.addWidget(lbl_title)

        pg.setConfigOption("background", "#0b0f19")
        pg.setConfigOption("foreground", "#f1f5f9")

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(0, 5)
        self.plot_widget.getAxis("left").setTicks([[(i, str(i)) for i in range(6)]])
        self.plot_widget.showGrid(x=False, y=True, alpha=0.2)
        self.plot_widget.setMouseEnabled(x=False, y=False)

        layout.addWidget(self.plot_widget)
        self.draw_chart()

    def init_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)
        layout.setContentsMargins(0, 5, 0, 0)
        self.settings_panel = SettingsWindow(self.repository, self.on_settings_saved)
        layout.addWidget(self.settings_panel)

    def draw_chart(self):
        data = self.repository.get_last_7_days_data()
        x_values = list(range(len(data)))
        y_values = list(data.values())
        date_labels = list(data.keys())
        short_dates = [d[5:] for d in date_labels]

        x_axis = self.plot_widget.getAxis("bottom")
        x_axis.setTicks([list(zip(x_values, short_dates))])

        bar_chart = pg.BarGraphItem(
            x=x_values, height=y_values, width=0.6, brush=pg.mkBrush(color=(16, 185, 129))
        )
        self.plot_widget.addItem(bar_chart)

    def update_progress_ui(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        count = self.repository.get_completed_count(today_str)
        self.daily_progress.setValue(count)
        self.lbl_progress_text.setText(f"Today: {count}/5 Completed")

    def show_then_raise(self) -> None:
        """Show the dashboard and bring it to the front. Safe to call repeatedly."""
        self.show()
        self.raise_()
        self.activateWindow()

    def populate_prayers(self, today_times: DailyPrayerTimes):
        for i in reversed(range(self.prayer_list_layout.count())):
            w = self.prayer_list_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        prayers = [
            ("Fajr", today_times.fajr),
            ("Dhuhr", today_times.dhuhr),
            ("Asr", today_times.asr),
            ("Maghrib", today_times.maghrib),
            ("Isha", today_times.isha),
        ]
        today_str = datetime.now().strftime("%Y-%m-%d")

        for name, time_obj in prayers:
            record = self.repository.get_record(today_str, name)
            is_completed = record.is_completed if record else False

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(4, 1, 4, 1)

            chk_box = QCheckBox(name)
            chk_box.setChecked(is_completed)
            chk_box.setCursor(Qt.CursorShape.PointingHandCursor)

            lbl_time = QLabel(time_obj.strftime("%I:%M %p"))
            lbl_time.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 500;")
            lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            row_layout.addWidget(chk_box)
            row_layout.addWidget(lbl_time)
            self.prayer_list_layout.addWidget(row_widget)

            chk_box.toggled.connect(
                lambda checked, p_name=name: self.handle_checkbox_toggle(p_name, checked)
            )

        # Update reference time display labels
        self.lbl_sunrise_val.setText(today_times.sunrise.strftime("%I:%M %p"))
        self.lbl_tahajjud_val.setText(today_times.tahajjud_start.strftime("%I:%M %p"))

    def update_statistics(self):
        current_streak = self.repository.get_current_streak()
        self.lbl_streak.setText(f"🔥 {current_streak}d Streak")

        today = datetime.now()
        month_data = self.repository.get_monthly_data(today.year, today.month)
        self.heatmap.update_data(today.year, today.month, month_data)

        self.plot_widget.clear()
        self.draw_chart()

    def handle_checkbox_toggle(self, prayer_name: str, is_completed: bool):
        today_str = datetime.now().strftime("%Y-%m-%d")
        record = PrayerRecord(
            date=today_str,
            prayer_name=prayer_name,
            is_completed=is_completed,
            completed_at=datetime.now() if is_completed else None,
        )
        self.repository.save_record(record)
        self.update_progress_ui()
        self.update_statistics()
