"""
Smoke test for DesktopNotifier.

The notifier shells out to `notify-send`. We monkey-patch subprocess.run
to avoid actually spawning a process and verify the call shape.
"""

from __future__ import annotations

from unittest.mock import patch

from app.notifications.notifier import DesktopNotifier


def test_send_invokes_notify_send_with_expected_args():
    with patch("app.notifications.notifier.subprocess.run") as mock_run:
        DesktopNotifier.send(
            title="Time for Prayer",
            message="It is now time for Fajr prayer.",
            icon_name="appointment-new",
        )
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert cmd[0] == "notify-send"
    assert "-a" in cmd
    assert "Prayer Companion" in cmd
    assert "-i" in cmd
    assert "appointment-new" in cmd
    assert "Time for Prayer" in cmd
    assert "It is now time for Fajr prayer." in cmd


def test_send_uses_default_icon_when_not_provided():
    with patch("app.notifications.notifier.subprocess.run") as mock_run:
        DesktopNotifier.send(title="x", message="y")
    cmd = mock_run.call_args[0][0]
    # Default icon_name is "appointment-new"
    assert "appointment-new" in cmd


def test_send_does_not_raise_when_notify_send_missing():
    """FileNotFoundError from subprocess.run should be swallowed, not raised."""
    with patch(
        "app.notifications.notifier.subprocess.run",
        side_effect=FileNotFoundError("notify-send not found"),
    ):
        # Should not raise.
        DesktopNotifier.send(title="x", message="y")


def test_send_swallows_generic_subprocess_exception():
    """Other subprocess exceptions should also be swallowed and logged."""
    with patch(
        "app.notifications.notifier.subprocess.run",
        side_effect=RuntimeError("something went wrong"),
    ):
        # Should not raise.
        DesktopNotifier.send(title="x", message="y")
