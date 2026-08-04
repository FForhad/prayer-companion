"""
Smoke tests for PrayerCalculationService.

These don't pin exact prayer times (adhanpy's outputs depend on a published
algorithm we'd need to snapshot) but they verify the cache and re-compute
behavior contract the rest of the app depends on.
"""

from __future__ import annotations

import datetime as _dt

from app.services.prayer_service import PrayerCalculationService


def test_cache_returns_same_object():
    svc = PrayerCalculationService(
        latitude=24.7471,
        longitude=90.4203,
        method_name="KARACHI",
        is_hanafi_asr=True,
    )
    a = svc.get_prayer_times(_dt.date(2026, 1, 15))
    b = svc.get_prayer_times(_dt.date(2026, 1, 15))
    # Cache returns the same instance — same object, equal contents.
    assert a is b


def test_clear_cache_forces_recompute():
    svc = PrayerCalculationService(
        latitude=24.7471,
        longitude=90.4203,
        method_name="KARACHI",
        is_hanafi_asr=True,
    )
    target = _dt.date(2026, 1, 15)
    a = svc.get_prayer_times(target)
    svc.clear_cache()
    b = svc.get_prayer_times(target)
    # After clear_cache, the new object is different but equal.
    assert a is not b
    assert a == b


def test_two_dates_each_get_their_own_cache_entry():
    svc = PrayerCalculationService(
        latitude=24.7471,
        longitude=90.4203,
        method_name="KARACHI",
        is_hanafi_asr=True,
    )
    today = svc.get_prayer_times(_dt.date(2026, 1, 15))
    tomorrow = svc.get_prayer_times(_dt.date(2026, 1, 16))
    assert today is not tomorrow


def test_dhaka_falls_inside_bd_bbox():
    svc = PrayerCalculationService(
        latitude=24.7471,
        longitude=90.4203,
        method_name="KARACHI",
        is_hanafi_asr=True,
    )
    # Should resolve to Asia/Dhaka.
    assert svc.tz.key == "Asia/Dhaka"


def test_london_outside_bd_bbox_uses_local_time():
    svc = PrayerCalculationService(
        latitude=51.5074,
        longitude=-0.1278,
        method_name="MWL",
        is_hanafi_asr=True,
    )
    # Outside Bangladesh bbox; we don't pin which tz, just assert it's a real tz.
    assert svc.tz is not None
