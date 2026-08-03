from datetime import datetime
from app.core.models import DailyPrayerTimes

class PrayerTracker:
    """
    Handles the logic for determining the current prayer, next prayer,
    and calculating the countdown and progress percentage.
    """
    
    @staticmethod
    def get_status(today_times: DailyPrayerTimes, tomorrow_times: DailyPrayerTimes, now: datetime):
        """
        Returns a tuple: (current_prayer_name, next_prayer_name, countdown_string, progress_percentage, seconds_left)
        """
        timeline = [
            ("Fajr", today_times.fajr),
            ("Sunrise", today_times.sunrise),
            ("Dhuhr", today_times.dhuhr),
            ("Asr", today_times.asr),
            ("Maghrib", today_times.maghrib),
            ("Isha", today_times.isha),
            ("Fajr (Tomorrow)", tomorrow_times.fajr)
        ]

        current_prayer = "Isha (Yesterday)"
        next_prayer = timeline[0][0]
        previous_time = now.replace(hour=0, minute=0, second=0) 
        next_time = timeline[0][1]

        for i in range(len(timeline) - 1):
            if timeline[i][1] <= now < timeline[i+1][1]:
                current_prayer = timeline[i][0]
                previous_time = timeline[i][1]
                
                next_prayer = timeline[i+1][0]
                next_time = timeline[i+1][1]
                break
        else:
            if now >= timeline[5][1]:
                current_prayer = "Isha"
                previous_time = timeline[5][1]
                next_prayer = timeline[6][0]
                next_time = timeline[6][1]

        time_left = next_time - now
        seconds_left = time_left.total_seconds() # NEW: Get raw seconds
        
        hours, remainder = divmod(seconds_left, 3600)
        minutes, seconds = divmod(remainder, 60)
        countdown_str = f"-{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        total_duration = (next_time - previous_time).total_seconds()
        elapsed_duration = (now - previous_time).total_seconds()
        
        progress_pct = 0
        if total_duration > 0:
            progress_pct = int((elapsed_duration / total_duration) * 100)

        # NEW: Now returns 5 items
        return current_prayer, next_prayer, countdown_str, progress_pct, seconds_left