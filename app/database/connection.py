import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

# Store database in the user's home directory (standard for Linux apps)
DB_DIR = Path.home() / ".local" / "share" / "prayer-companion"
DB_PATH = DB_DIR / "prayer_companion.db"


def initialize_database() -> None:
    """
    Creates the database directory and initializes tables if they don't exist.
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Enable Write-Ahead Logging for better performance
        cursor.execute("PRAGMA journal_mode=WAL;")

        # Prayer Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prayer_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                prayer_name TEXT NOT NULL,
                is_completed BOOLEAN NOT NULL DEFAULT 0,
                completed_at TIMESTAMP,
                is_jamaah BOOLEAN NOT NULL DEFAULT 0,
                is_late BOOLEAN NOT NULL DEFAULT 0,
                notes TEXT,
                UNIQUE(date, prayer_name)
            )
        """)

        # Settings table (Key-Value store)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Ensures connections are properly closed after use.
    """
    # FIX: Removed detect_types=sqlite3.PARSE_DECLTYPES to prevent the ValueError
    conn = sqlite3.connect(DB_PATH)

    # Return rows as dictionaries instead of tuples for easier access
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
