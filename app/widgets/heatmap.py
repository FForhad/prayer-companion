import calendar

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class MonthlyHeatmapWidget(QWidget):
    """
    A widget that displays a GitHub-style contribution graph for a single month.
    """

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_title = QLabel("Monthly Activity")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #CCCCCC;")
        self.layout.addWidget(self.lbl_title)

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(4)  # Space between squares
        self.layout.addWidget(self.grid_container)

    def update_data(self, year: int, month: int, data: dict):
        """
        Redraws the heatmap based on the provided data.
        data: dict mapping 'YYYY-MM-DD' to completed count (0-5)
        """
        # Clear existing grid
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.lbl_title.setText(f"{calendar.month_name[month]} {year} Activity")

        _, num_days = calendar.monthrange(year, month)

        # We'll organize it roughly like a calendar (7 columns)
        row = 0
        col = 0

        for day in range(1, num_days + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            completed_count = data.get(date_str, 0)

            # Determine color based on completion
            if completed_count == 0:
                color = "#2D2D2D"  # Empty/Gray
            elif completed_count <= 2:
                color = "#7CB342"  # Light Green
            elif completed_count <= 4:
                color = "#43A047"  # Medium Green
            else:
                color = "#1B5E20"  # Dark Green (Perfect day)

            square = QFrame()
            square.setFixedSize(16, 16)
            square.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            square.setToolTip(f"{date_str}: {completed_count}/5 prayers")  # Hover text

            self.grid.addWidget(square, row, col)

            row += 1
            if row > 4:  # 5 rows tall, similar to GitHub
                row = 0
                col += 1
