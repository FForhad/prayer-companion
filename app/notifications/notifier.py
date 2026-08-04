import logging
import subprocess


class DesktopNotifier:
    """
    Handles native Linux desktop notifications using notify-send.
    This works across GNOME, KDE, XFCE, and other standard desktop environments.
    """

    @staticmethod
    def send(title: str, message: str, icon_name: str = "appointment-new"):
        """
        Sends a desktop notification.
        :param title: The title of the notification.
        :param message: The body text of the notification.
        :param icon_name: A system icon name (e.g., 'appointment-new', 'info').
        """
        try:
            # -a sets the App Name in the notification center
            # -i sets the icon
            # -u sets the urgency (normal)
            subprocess.run(
                [
                    "notify-send",
                    "-a",
                    "Prayer Companion",
                    "-i",
                    icon_name,
                    "-u",
                    "normal",
                    title,
                    message,
                ],
                check=False,
            )
        except FileNotFoundError:
            logging.error("notify-send command not found. Please install libnotify-bin.")
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")
