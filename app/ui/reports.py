import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from app.database.repository import PrayerLogRepository

class ReportsWindow(QWidget):
    """
    A dedicated window for viewing charts and analytics.
    """
    def __init__(self, repository: PrayerLogRepository):
        super().__init__()
        self.repository = repository
        
        self.setWindowTitle("Prayer Companion - Analytics")
        self.resize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.lbl_header = QLabel("Weekly Completion Chart")
        self.lbl_header.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.lbl_header)

        # Configure PyQtGraph globally
        pg.setConfigOption('background', '#121212') # Match our dark theme
        pg.setConfigOption('foreground', '#FFFFFF')

        # Create the Plot Widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        
        # Customize the plot
        self.plot_widget.setYRange(0, 5) # Prayers only go up to 5
        self.plot_widget.getAxis('left').setTicks([[(i, str(i)) for i in range(6)]])
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        self.plot_widget.setMouseEnabled(x=False, y=False) # Disable panning/zooming

        self.draw_chart()

    def draw_chart(self):
        data = self.repository.get_last_7_days_data()
        
        # Extract X (indices) and Y (counts)
        x_values = list(range(len(data)))
        y_values = list(data.values())
        date_labels = list(data.keys())

        # Format dates from 'YYYY-MM-DD' to 'MM-DD' for cleaner X-axis labels
        short_dates = [d[5:] for d in date_labels]
        
        # Set X-axis labels
        x_axis = self.plot_widget.getAxis('bottom')
        ticks = [list(zip(x_values, short_dates))]
        x_axis.setTicks(ticks)

        # Draw the Bar Graph
        bar_chart = pg.BarGraphItem(
            x=x_values, 
            height=y_values, 
            width=0.6, 
            brush=pg.mkBrush(color=(76, 175, 80)) # #4CAF50 Green
        )
        self.plot_widget.addItem(bar_chart)