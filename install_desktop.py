import os
import sys
from pathlib import Path

def install_desktop_integration():
    """Generates and installs Linux .desktop files for the application."""
    
    # 1. Get the absolute path of the project directory (assuming this script is in project root or app root)
    # If this script is inside 'app/', use Path(__file__).parent.parent.absolute()
    project_dir = Path(__file__).parent.absolute()
    
    # 2. Get the path to the currently active python executable
    venv_python = sys.executable
    
    # 3. Define the absolute path to your custom icon file
    icon_path = project_dir / "app" / "assets" / "time.png"
    
    # 4. Define the .desktop file content
    desktop_file_content = f"""[Desktop Entry]
Name=PrayerTimer
Comment=Islamic Prayer Tracker and Countdown
Exec={venv_python} -m app.main
Path={project_dir}
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;Education;
Keywords=Prayer;Islam;Muslim;Adhan;
"""

    # 5. Install to the local applications directory
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file_path = apps_dir / "prayer-companion.desktop"
    
    with open(desktop_file_path, "w") as f:
        f.write(desktop_file_content)
        
    desktop_file_path.chmod(0o755)
    
    print(f"✅ Successfully installed App Launcher entry to: {desktop_file_path}")
    print("You should now be able to search for 'PrayerTimer' in your application menu with your custom icon.")

    # 6. Ask about Auto-Start
    autostart = input("\nDo you want PrayerTimer to start automatically when you log in? (y/n): ").strip().lower()
    
    if autostart == 'y':
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        autostart_path = autostart_dir / "prayer-companion.desktop"
        
        with open(autostart_path, "w") as f:
            f.write(desktop_file_content)
            
        autostart_path.chmod(0o755)
        print(f"✅ Successfully installed Auto-Start entry to: {autostart_path}")
    else:
        print("Skipped Auto-Start installation.")

if __name__ == "__main__":
    install_desktop_integration()