from datetime import date, timedelta
from zoneinfo import ZoneInfo

from app.core.models import DailyPrayerTimes

adlib = None
try:
    from adhanpy.calculation.CalculationParameters import CalculationParameters
    from adhanpy.calculation.Madhab import Madhab
    from adhanpy.PrayerTimes import PrayerTimes
    adlib = True
except ImportError:
    adlib = False

class PrayerCalculationService:
    def __init__(self, latitude: float, longitude: float, method_name: str = "KARACHI", is_hanafi_asr: bool = True):
        from datetime import datetime  # local import to keep module surface small

        self.latitude = latitude
        self.longitude = longitude
        self.method_name = method_name
        self.is_hanafi_asr = is_hanafi_asr

        if 88.0 <= longitude <= 93.0 and 20.0 <= latitude <= 27.0:
            self.tz = ZoneInfo("Asia/Dhaka")
        else:
            self.tz = datetime.now().astimezone().tzinfo

        # Per-day cache so the 1Hz UI tick doesn't recompute adhanpy every second.
        self._cache: dict[date, DailyPrayerTimes] = {}

    def get_params(self):
        if not adlib:
            raise ImportError("adhanpy is not installed.")
            
        if self.method_name == "MUSLIM_WORLD_LEAGUE":
            params = CalculationParameters(fajr_angle=18.0, isha_angle=17.0)
        elif self.method_name == "ISNA":
            params = CalculationParameters(fajr_angle=15.0, isha_angle=15.0)
        elif self.method_name == "UMM_AL_QURA":
            params = CalculationParameters(fajr_angle=18.5, isha_angle=18.5)
        elif self.method_name == "EGYPTIAN":
            params = CalculationParameters(fajr_angle=19.5, isha_angle=17.5)
        else:
            params = CalculationParameters(fajr_angle=18.0, isha_angle=18.0)
            
        params.madhab = Madhab.HANAFI if self.is_hanafi_asr else Madhab.SHAFI
        return params

    def _compute(self, target_date: date) -> DailyPrayerTimes:
        """Heavy path: run adhanpy and compute the tahajjud window."""
        params = self.get_params()

        pt = PrayerTimes(
            (self.latitude, self.longitude),
            target_date,
            calculation_parameters=params,
            time_zone=self.tz,
        )

        # Calculate Tahajjud (Last 1/3 of the night starting from today's Maghrib to tomorrow's Fajr)
        tomorrow_date = target_date + timedelta(days=1)
        pt_tomorrow = PrayerTimes(
            (self.latitude, self.longitude),
            tomorrow_date,
            calculation_parameters=params,
            time_zone=self.tz,
        )

        night_duration = pt_tomorrow.fajr - pt.maghrib
        tahajjud_start = pt_tomorrow.fajr - (night_duration / 3)

        return DailyPrayerTimes(
            fajr=pt.fajr,
            sunrise=pt.sunrise,
            dhuhr=pt.dhuhr,
            asr=pt.asr,
            maghrib=pt.maghrib,
            isha=pt.isha,
            tahajjud_start=tahajjud_start,
        )

    def get_prayer_times(self, target_date: date) -> DailyPrayerTimes:
        """Cached lookup. Cache is invalidated by clear_cache() on settings change."""
        cached = self._cache.get(target_date)
        if cached is not None:
            return cached
        times = self._compute(target_date)
        self._cache[target_date] = times
        return times

    def clear_cache(self) -> None:
        """Drop all cached days. Call after settings (lat/lon/method/madhab) change."""
        self._cache.clear()