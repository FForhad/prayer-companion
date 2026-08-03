from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication

class FloatingWidget(QWidget):
    menu_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(280, 80)

        # Sleek modern dark theme with an emerald accent bar on the left
        self.setStyleSheet("""
            QWidget#MainCard {
                background-color: rgba(13, 17, 23, 245);
                border: 1px solid #1f2937;
                border-left: 4px solid #10b981;
                border-radius: 10px;
            }
            QLabel {
                color: #f1f5f9;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QPushButton#ActionBtn {
                background-color: transparent;
                color: #94a3b8;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 4px;
            }
            QPushButton#ActionBtn:hover {
                color: #ffffff;
                background-color: rgba(255, 255, 255, 20);
            }
            QPushButton#CloseBtn {
                background-color: transparent;
                color: #94a3b8;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 4px;
            }
            QPushButton#CloseBtn:hover {
                color: #ffffff;
                background-color: #ef4444;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card = QWidget()
        self.card.setObjectName("MainCard")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(12, 8, 8, 8)
        card_layout.setSpacing(2)

        # Top row: Current Prayer + Menu & Close buttons
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_current = QLabel("Fajr")
        self.lbl_current.setStyleSheet("font-size: 13px; font-weight: 700; color: #38bdf8;")
        top_row.addWidget(self.lbl_current)
        top_row.addStretch()

        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setObjectName("ActionBtn")
        self.btn_menu.setFixedSize(20, 20)
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.clicked.connect(self.menu_clicked.emit)
        top_row.addWidget(self.btn_menu)

        self.btn_close = QPushButton("×")
        self.btn_close.setObjectName("CloseBtn")
        self.btn_close.setFixedSize(20, 20)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(QApplication.quit)
        top_row.addWidget(self.btn_close)

        card_layout.addLayout(top_row)

        # Middle row: Countdown info
        self.lbl_countdown = QLabel("02:15:30 remaining")
        self.lbl_countdown.setStyleSheet("font-size: 13px; font-weight: 600; color: #f8fafc;")
        card_layout.addWidget(self.lbl_countdown)

        # Bottom row: Next prayer info
        self.lbl_next = QLabel("Next: Dhuhr at 12:15 PM")
        self.lbl_next.setStyleSheet("font-size: 11px; color: #94a3b8;")
        card_layout.addWidget(self.lbl_next)

        layout.addWidget(self.card)

        # Window dragging support
        self.old_pos = None

    def update_display(self, current_prayer, next_prayer, countdown_str, progress):
        self.lbl_current.setText(current_prayer)
        self.lbl_countdown.setText(f"{countdown_str} remaining")
        self.lbl_next.setText(f"Next: {next_prayer}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None