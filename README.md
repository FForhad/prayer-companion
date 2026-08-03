# 🌙 Prayer Companion (PrayerTimer)

A modern, lightweight, and elegant Linux desktop application built with **Python** and **PySide6** to track Islamic prayer times, view real-time countdowns, log daily prayers, and visualize prayer consistency with beautiful analytics.

Designed especially for Linux users, Prayer Companion includes a sleek floating desktop widget that stays on top of your workspace, allowing you to monitor prayer times without interrupting your workflow.

---

# ✨ Features

## 🪟 Floating Desktop Widget

- Frameless, translucent, and draggable
- Always stays on top
- Live countdown to the next prayer
- Quick-access menu (`⋮`) to open the dashboard
- Close button (`×`)

## 🕌 High-Precision Prayer Time Calculations

Powered by **adhanpy** with support for:

- Muslim World League
- Karachi
- ISNA
- Umm al-Qura
- Egyptian General Authority

Supports both:

- Hanafi Asr
- Shafi Asr

## 🌍 Worldwide Location Support

- Built-in presets for all **64 districts of Bangladesh**
- Popular international cities:
  - Makkah
  - Madinah
  - London
  - New York
  - Dubai
  - Kuala Lumpur
- Manual latitude & longitude input

## 📊 Dashboard & Analytics

### Today

- Daily prayer check-ins
- Current streak
- Daily progress bar
- Special & Reference Times
  - Sunrise
  - Tahajjud (Last third of the night)

### Analytics

- Weekly performance charts
- Monthly GitHub-style prayer heatmap
- Prayer consistency tracking

## 🐧 Linux Desktop Integration

Includes an installer that automatically:

- Creates a `.desktop` launcher
- Registers the application in the application menu
- Uses a custom icon
- Optionally enables auto-start on login

---

# 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| GUI | PySide6 (Qt for Python) |
| Prayer Calculations | adhanpy |
| Charts | pyqtgraph |
| Database | SQLite |

---

# 📁 Project Structure

```text
prayer-companion/
├── app/
│   ├── assets/          # Icons and images (e.g. time.png)
│   ├── core/            # Prayer state tracker & business logic
│   ├── database/        # SQLite connection and repositories
│   ├── notifications/   # Linux desktop notifications
│   ├── services/        # adhanpy wrapper and location services
│   ├── ui/              # Dashboard, floating widget, system tray
│   └── main.py          # Application entry point
├── install_desktop.py   # Linux desktop integration
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/FForhad/prayer-companion.git
cd prayer-companion
```

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Application

```bash
python -m app.main
```

---

# 🖥 Linux Desktop Integration

To add Prayer Companion to your Linux application menu and optionally enable auto-start on login:

```bash
python install_desktop.py
```

The installer will automatically:

- Create a `.desktop` launcher
- Register it under:

```text
~/.local/share/applications/
```

- Use the application icon:

```text
app/assets/time.png
```

---

# ⚙ Configuration

You can configure the following from the **Settings** tab inside the dashboard:

- Location
- Calculation Method
- Madhab (Hanafi/Shafi)
- Notification preferences

Open the dashboard anytime by clicking the **⋮** button on the floating widget.

---

# 🤝 Contributing

Contributions are welcome!

If you'd like to improve Prayer Companion:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

Bug reports and feature requests are also appreciated.

---

# 📄 License

This project is licensed under the **MIT License**.

---

**May this project help Muslims maintain consistency in their daily prayers. 🤲**