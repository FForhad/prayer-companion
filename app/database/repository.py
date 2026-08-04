from datetime import date, datetime, timedelta
from typing import List, Optional
from app.core.models import PrayerRecord
from app.database.connection import get_db_connection

class PrayerLogRepository:
    """
    Handles CRUD operations for daily prayer records.
    """

    def get_record(self, target_date: str, prayer_name: str) -> Optional[PrayerRecord]:
        """Fetch a specific prayer record by date and name."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM prayer_logs WHERE date = ? AND prayer_name = ?",
                (target_date, prayer_name)
            )
            row = cursor.fetchone()
            
            if row:
                return PrayerRecord(
                    date=row["date"],
                    prayer_name=row["prayer_name"],
                    is_completed=bool(row["is_completed"]),
                    completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
                    is_jamaah=bool(row["is_jamaah"]),
                    is_late=bool(row["is_late"]),
                    notes=row["notes"]
                )
            return None

    def save_record(self, record: PrayerRecord) -> None:
        """Insert a new record or update an existing one (Upsert)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            completed_at_str = record.completed_at.isoformat() if record.completed_at else None
            
            cursor.execute(
                """
                INSERT INTO prayer_logs (date, prayer_name, is_completed, completed_at, is_jamaah, is_late, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, prayer_name) DO UPDATE SET
                    is_completed=excluded.is_completed,
                    completed_at=excluded.completed_at,
                    is_jamaah=excluded.is_jamaah,
                    is_late=excluded.is_late,
                    notes=excluded.notes
                """,
                (
                    record.date,
                    record.prayer_name,
                    record.is_completed,
                    completed_at_str,
                    record.is_jamaah,
                    record.is_late,
                    record.notes
                )
            )
            conn.commit()

    def get_completed_count(self, target_date: str) -> int:
        """Returns the number of completed prayers for a specific date."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM prayer_logs WHERE date = ? AND is_completed = 1",
                (target_date,)
            )
            row = cursor.fetchone()
            return row["count"] if row else 0
        
    def get_longest_streak(self) -> int:
        """
        Longest run of consecutive days on which all 5 prayers were completed
        (a "perfect day"). Days with 1-4 prayers do not count toward this streak.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # This query finds dates where the count of completed prayers is 5
            cursor.execute("""
                WITH DailyCounts AS (
                    SELECT date, COUNT(*) as completed_count
                    FROM prayer_logs
                    WHERE is_completed = 1
                    GROUP BY date
                ),
                PerfectDays AS (
                    SELECT date
                    FROM DailyCounts
                    WHERE completed_count = 5
                )
                SELECT date FROM PerfectDays ORDER BY date
            """)
            rows = cursor.fetchall()

            if not rows:
                return 0

            max_streak = 1
            current_streak = 1
            
            # Simple python loop to count consecutive days
            for i in range(1, len(rows)):
                prev_date = datetime.strptime(rows[i-1]["date"], "%Y-%m-%d").date()
                curr_date = datetime.strptime(rows[i]["date"], "%Y-%m-%d").date()
                
                if (curr_date - prev_date).days == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1

            return max_streak

    def get_current_streak(self) -> int:
        """
        Current active streak of consecutive "perfect days" (all 5 prayers
        completed), anchored on today or yesterday.

        - If today is a perfect day, the streak counts back from today.
        - Else if yesterday is a perfect day, the streak counts back from yesterday
          (the user hasn't broken the streak yet today).
        - Otherwise returns 0.

        Uses the same strict 5/5 definition as get_longest_streak.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date
                FROM prayer_logs
                WHERE is_completed = 1
                GROUP BY date
                HAVING COUNT(*) = 5
                ORDER BY date DESC
            """)
            perfect_dates = {
                datetime.strptime(row["date"], "%Y-%m-%d").date()
                for row in cursor.fetchall()
            }

        if not perfect_dates:
            return 0

        # Anchor: most recent perfect date must be today or yesterday.
        if today in perfect_dates:
            anchor = today
        elif yesterday in perfect_dates:
            anchor = yesterday
        else:
            return 0

        streak = 0
        cursor_date = anchor
        while cursor_date in perfect_dates:
            streak += 1
            cursor_date -= timedelta(days=1)

        return streak
         
    def get_monthly_data(self, year: int, month: int) -> dict:
        """
        Returns a dictionary mapping 'YYYY-MM-DD' to the number of completed prayers (0-5)
        for a specific month. This is used for the heatmap.
        """
        month_str = f"{year:04d}-{month:02d}"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, COUNT(*) as completed_count
                FROM prayer_logs
                WHERE date LIKE ? AND is_completed = 1
                GROUP BY date
            """, (f"{month_str}-%",))
            
            rows = cursor.fetchall()
            return {row["date"]: row["completed_count"] for row in rows}
    
    def get_last_7_days_data(self) -> dict:
        """
        Returns a dictionary of the last 7 dates and their completion count.
        Example: {'2023-10-20': 5, '2023-10-21': 4, ...}
        """
        import datetime
        
        today = datetime.date.today()
        dates_to_fetch = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        # Initialize dictionary with 0s so days with no records still show up on the chart
        results = {date: 0 for date in dates_to_fetch}
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Fetch data for these specific dates
            placeholders = ",".join("?" * len(dates_to_fetch))
            cursor.execute(f"""
                SELECT date, COUNT(*) as count 
                FROM prayer_logs 
                WHERE date IN ({placeholders}) AND is_completed = 1
                GROUP BY date
            """, dates_to_fetch)
            
            for row in cursor.fetchall():
                results[row["date"]] = row["count"]
                
        return results
    
    def get_setting(self, key: str, default_value: str = None) -> str:
        """Fetches a setting from the database, or returns the default."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default_value

    def save_setting(self, key: str, value: str) -> None:
        """Saves or updates a setting in the database."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))
            conn.commit()