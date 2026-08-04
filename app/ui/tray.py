import sys
from pathlib import Path
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication

# Bundled icon — works on any desktop environment regardless of theme.
ICON_PATH = Path(__file__).resolve().parent.parent / "assets" / "time.png"


class AppTrayIcon(QSystemTrayIcon):
    """
    Manages the system tray icon for Linux desktop environments.
    Allows the user to hide/show the app and quit completely.
    """
    def __init__(self, dashboard, floating_widget):
        icon = QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QIcon.fromTheme("appointment-new")
        super().__init__(icon)
        
        self.dashboard = dashboard
        self.floating_widget = floating_widget
        
        # Create the right-click menu
        self.menu = QMenu()
        
        self.toggle_dashboard_action = QAction("Toggle Dashboard")
        self.toggle_dashboard_action.triggered.connect(self.toggle_dashboard)
        self.menu.addAction(self.toggle_dashboard_action)
        
        self.toggle_widget_action = QAction("Toggle Widget")
        self.toggle_widget_action.triggered.connect(self.toggle_widget)
        self.menu.addAction(self.toggle_widget_action)
        
        self.menu.addSeparator()
        
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)

    def toggle_dashboard(self):
        if self.dashboard.isVisible():
            self.dashboard.hide()
        else:
            self.dashboard.show()
            self.dashboard.raise_()
            self.dashboard.activateWindow()

    def toggle_widget(self):
        if self.floating_widget.isVisible():
            self.floating_widget.hide()
        else:
            self.floating_widget.show()

    def quit_app(self):
        QApplication.quit()
        sys.exit()