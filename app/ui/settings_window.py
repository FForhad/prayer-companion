from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.database.repository import PrayerLogRepository


class SettingsWindow(QWidget):
    # Complete collection of all 64 districts of Bangladesh + international hubs
    CITIES = {
        "--- Select District / City ---": (None, None),
        # International Hubs
        "Makkah, Saudi Arabia": (21.3891, 39.8579),
        "Medina, Saudi Arabia": (24.4539, 39.6333),
        "London, United Kingdom": (51.5074, -0.1278),
        "New York, USA": (40.7128, -74.0060),
        "Dubai, UAE": (25.2048, 55.2708),
        "Kuala Lumpur, Malaysia": (3.1390, 101.6869),
        # All 64 Districts of Bangladesh (Alphabetical)
        "Bagerhat, Bangladesh": (22.6602, 89.7895),
        "Bandarban, Bangladesh": (21.8311, 92.3686),
        "Barguna, Bangladesh": (22.0953, 90.1121),
        "Barishal, Bangladesh": (22.7029, 90.3466),
        "Bhola, Bangladesh": (22.1785, 90.7101),
        "Bogura, Bangladesh": (24.8436, 89.3701),
        "Brahmanbaria, Bangladesh": (23.9608, 91.1115),
        "Chandpur, Bangladesh": (23.2513, 90.8518),
        "Chattogram, Bangladesh": (22.3475, 91.8123),
        "Chuadanga, Bangladesh": (23.6161, 88.8263),
        "Cox's Bazar, Bangladesh": (21.4395, 92.0077),
        "Cumilla, Bangladesh": (23.4619, 91.1869),
        "Dhaka, Bangladesh": (23.7289, 90.3944),
        "Dinajpur, Bangladesh": (25.6279, 88.6332),
        "Faridpur, Bangladesh": (23.5986, 89.8353),
        "Feni, Bangladesh": (23.0159, 91.3976),
        "Gaibandha, Bangladesh": (25.3297, 89.5430),
        "Gazipur, Bangladesh": (23.9889, 90.3750),
        "Gopalganj, Bangladesh": (23.0000, 89.8167),
        "Habiganj, Bangladesh": (24.4771, 91.4507),
        "Jamalpur, Bangladesh": (24.9197, 89.9481),
        "Jashore, Bangladesh": (23.1634, 89.2182),
        "Jhalokati, Bangladesh": (22.5721, 90.1870),
        "Jhenaidah, Bangladesh": (23.5450, 89.1726),
        "Joypurhat, Bangladesh": (25.0947, 89.0945),
        "Khagrachhari, Bangladesh": (23.1322, 91.9490),
        "Khulna, Bangladesh": (22.8456, 89.5403),
        "Kishoreganj, Bangladesh": (24.4260, 90.9821),
        "Kurigram, Bangladesh": (25.8072, 89.6295),
        "Kushtia, Bangladesh": (23.8907, 89.1099),
        "Lakshmipur, Bangladesh": (22.9447, 90.8282),
        "Lalmonirhat, Bangladesh": (25.9923, 89.2847),
        "Madaripur, Bangladesh": (23.2393, 90.1870),
        "Magura, Bangladesh": (23.4855, 89.4198),
        "Manikganj, Bangladesh": (23.8617, 90.0003),
        "Meherpur, Bangladesh": (23.8052, 88.6724),
        "Moulvibazar, Bangladesh": (24.3095, 91.7315),
        "Munshiganj, Bangladesh": (23.4981, 90.4127),
        "Mymensingh, Bangladesh": (24.7434, 90.3984),
        "Naogaon, Bangladesh": (24.9132, 88.7531),
        "Narail, Bangladesh": (23.1657, 89.4990),
        "Narayanganj, Bangladesh": (23.6226, 90.4998),
        "Narsingdi, Bangladesh": (24.1344, 90.7860),
        "Natore, Bangladesh": (24.4102, 89.0076),
        "Netrokona, Bangladesh": (24.8103, 90.8656),
        "Nilphamari, Bangladesh": (25.8483, 88.9414),
        "Noakhali, Bangladesh": (22.8724, 91.0973),
        "Pabna, Bangladesh": (24.0113, 89.2562),
        "Panchagarh, Bangladesh": (26.2709, 88.5952),
        "Patuakhali, Bangladesh": (22.2249, 90.4548),
        "Pirojpur, Bangladesh": (22.5791, 89.9759),
        "Rajbari, Bangladesh": (23.7151, 89.5875),
        "Rajshahi, Bangladesh": (24.3636, 88.6241),
        "Rangamati, Bangladesh": (22.7324, 92.2985),
        "Rangpur, Bangladesh": (25.7439, 89.2752),
        "Satkhira, Bangladesh": (22.3155, 89.1115),
        "Shariatpur, Bangladesh": (23.2423, 90.4348),
        "Sherpur, Bangladesh": (25.0746, 90.1495),
        "Sirajganj, Bangladesh": (24.3141, 89.5700),
        "Sunamganj, Bangladesh": (25.0715, 91.3992),
        "Sylhet, Bangladesh": (24.9045, 91.8611),
        "Tangail, Bangladesh": (24.2450, 89.9113),
        "Thakurgaon, Bangladesh": (26.0418, 88.4283),
    }

    def __init__(self, repository: PrayerLogRepository, on_save_callback=None):
        super().__init__()
        self.repository = repository
        self.on_save_callback = on_save_callback

        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: #f1f5f9;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            QComboBox, QLineEdit {
                background-color: #131b2e;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
            QPushButton {
                background-color: #10b981;
                color: white;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px;
                margin-top: 15px;
            }
            QPushButton:hover { background-color: #059669; }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        header = QLabel("Preferences & Location")
        header.setStyleSheet(
            "font-size: 16px; font-weight: 700; margin-bottom: 5px; color: #ffffff;"
        )
        self.layout.addWidget(header)

        # Form Layout for Inputs
        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(12)

        # 1. District / City Quick-Select Dropdown
        self.combo_city = QComboBox()
        self.combo_city.addItems(list(self.CITIES.keys()))
        self.combo_city.currentTextChanged.connect(self.on_city_selected)
        self.form_layout.addRow("Quick Preset:", self.combo_city)

        # 2. Latitude Box
        saved_lat = self.repository.get_setting("latitude", "24.7471")
        self.inp_lat = QLineEdit()
        self.inp_lat.setText(saved_lat)
        self.form_layout.addRow("Latitude:", self.inp_lat)

        # 3. Longitude Box
        saved_lon = self.repository.get_setting("longitude", "90.4203")
        self.inp_lon = QLineEdit()
        self.inp_lon.setText(saved_lon)
        self.form_layout.addRow("Longitude:", self.inp_lon)

        # Pre-select matching district if saved coordinates match one of them
        try:
            f_lat, f_lon = float(saved_lat), float(saved_lon)
            for city_name, (lat, lon) in self.CITIES.items():
                if lat is not None and abs(lat - f_lat) < 0.05 and abs(lon - f_lon) < 0.05:
                    self.combo_city.setCurrentText(city_name)
                    break
        except ValueError:
            pass

        # 4. Calculation Method Dropdown
        self.combo_method = QComboBox()
        methods = ["KARACHI", "MUSLIM_WORLD_LEAGUE", "ISNA", "UMM_AL_QURA", "EGYPTIAN"]
        self.combo_method.addItems(methods)
        current_method = self.repository.get_setting("calc_method", "KARACHI")
        if current_method in methods:
            self.combo_method.setCurrentText(current_method)
        self.form_layout.addRow("Method:", self.combo_method)

        # 5. Asr Madhab Checkbox
        self.chk_hanafi = QCheckBox("Use Hanafi Asr Time")
        is_hanafi = self.repository.get_setting("is_hanafi", "True") == "True"
        self.chk_hanafi.setChecked(is_hanafi)
        self.form_layout.addRow("", self.chk_hanafi)

        self.layout.addLayout(self.form_layout)
        self.layout.addStretch()

        # Save Button
        self.btn_save = QPushButton("Save & Apply Changes")
        self.btn_save.clicked.connect(self.save_settings)
        self.layout.addWidget(self.btn_save)

    def on_city_selected(self, city_name: str):
        """Automatically updates lat/lon boxes when a district is picked from the dropdown."""
        if city_name in self.CITIES and self.CITIES[city_name][0] is not None:
            lat, lon = self.CITIES[city_name]
            self.inp_lat.setText(str(lat))
            self.inp_lon.setText(str(lon))

    def save_settings(self):
        """Saves selected coordinates and configuration to the database."""
        try:
            lat = float(self.inp_lat.text())
            lon = float(self.inp_lon.text())

            self.repository.save_setting("latitude", str(lat))
            self.repository.save_setting("longitude", str(lon))
            self.repository.save_setting("calc_method", self.combo_method.currentText())
            self.repository.save_setting("is_hanafi", str(self.chk_hanafi.isChecked()))

            QMessageBox.information(
                self, "Success", f"Settings updated successfully!\nCoords: {lat}, {lon}"
            )

            if self.on_save_callback:
                self.on_save_callback()

        except ValueError:
            QMessageBox.critical(self, "Error", "Latitude and Longitude must be valid numbers.")
