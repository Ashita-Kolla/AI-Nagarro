import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trixie_wellness.db")

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. mood_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_logs (
        id          TEXT    PRIMARY KEY,
        user_input  TEXT    NOT NULL,
        stress_level TEXT   DEFAULT '',
        emotion     TEXT    DEFAULT '',
        severity    TEXT    DEFAULT '',
        cause       TEXT    DEFAULT '',
        sleep_hours REAL    DEFAULT NULL,
        timestamp   TEXT    NOT NULL
    )
    """)
    
    # 2. journal_metadata
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_metadata (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        emotion     TEXT    DEFAULT '',
        severity    TEXT    DEFAULT '',
        cause       TEXT    DEFAULT '',
        content     TEXT    NOT NULL,
        word_count  INTEGER DEFAULT 0,
        doc_url     TEXT    DEFAULT '',
        timestamp   TEXT    NOT NULL
    )
    """)
    
    # 3. reminders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id          TEXT    PRIMARY KEY,
        activity    TEXT    NOT NULL,
        time        TEXT    NOT NULL,
        frequency   TEXT    DEFAULT 'daily',
        active      INTEGER DEFAULT 1,
        timestamp   TEXT    NOT NULL
    )
    """)
    
    # 4. reminder_history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminder_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        reminder_id TEXT    NOT NULL,
        activity    TEXT    NOT NULL,
        action      TEXT    NOT NULL,
        timestamp   TEXT    NOT NULL
    )
    """)
    
    # Seed historical mock data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM mood_logs")
    if cursor.fetchone()[0] == 0:
        mock_moods = [
            ("mood_hist1", "I had a great morning jog and slept very well last night. Feeling ready for work.", "low", "happy", "low", "personal", 8.0, "2026-05-12T08:30:00"),
            ("mood_hist2", "Feeling extremely exhausted after back-to-back status meetings. Drained.", "medium", "tired", "medium", "meetings", 6.0, "2026-05-15T18:45:00"),
            ("mood_hist3", "A lot of deadlines are piling up. I feel stressed and slightly anxious about the release.", "medium", "stressed", "medium", "workload", 5.5, "2026-05-20T21:15:00"),
            ("mood_hist4", "Got a full 8 hours of sleep. Feeling very refreshed and positive today.", "low", "happy", "low", "personal", 8.0, "2026-05-24T10:00:00"),
            ("mood_hist5", "Too many tasks assigned at the last minute by my manager. I feel totally overwhelmed and can't cope.", "high", "overwhelmed", "high", "workload", 5.0, "2026-05-26T15:30:00")
        ]
        cursor.executemany("""
            INSERT INTO mood_logs (id, user_input, stress_level, emotion, severity, cause, sleep_hours, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, mock_moods)

    cursor.execute("SELECT COUNT(*) FROM journal_metadata")
    if cursor.fetchone()[0] == 0:
        mock_journals = [
            ("happy", "low", "personal", "Had an amazing morning jog. Feeling refreshed and ready to tackle the week ahead.", 13, "https://docs.google.com/document/d/1_TrixieWellnessJournal_MockID_abc123/edit", "2026-05-12 09:00:00"),
            ("tired", "medium", "meetings", "Ended up in back-to-back status meetings. My head is spinning, but glad it's Friday soon.", 15, "https://docs.google.com/document/d/1_TrixieWellnessJournal_MockID_abc123/edit", "2026-05-15 19:00:00"),
            ("stressed", "medium", "workload", "Too many deadlines overlapping. Need to start prioritizing task limits tomorrow.", 11, "https://docs.google.com/document/d/1_TrixieWellnessJournal_MockID_abc123/edit", "2026-05-20 22:00:00"),
            ("overwhelmed", "high", "workload", "Manager added three urgent assignments at 4 PM. Struggling to stay calm.", 12, "https://docs.google.com/document/d/1_TrixieWellnessJournal_MockID_abc123/edit", "2026-05-26 16:00:00")
        ]
        cursor.executemany("""
            INSERT INTO journal_metadata (emotion, severity, cause, content, word_count, doc_url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, mock_journals)
    
    conn.commit()
    conn.close()


# --- Mood Logs Operations ---

def save_mood_log(log_id: str, user_input: str, stress_level: str, emotion: str, severity: str, cause: str, sleep_hours: float, timestamp: str = None) -> bool:
    if not timestamp:
        timestamp = datetime.now().isoformat()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mood_logs (id, user_input, stress_level, emotion, severity, cause, sleep_hours, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (log_id, user_input, stress_level, emotion, severity, cause, sleep_hours, timestamp)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving mood log: {e}")
        return False

# --- Journal Metadata Operations ---

def save_journal_metadata(emotion: str, severity: str, cause: str, content: str, word_count: int, doc_url: str, timestamp: str = None) -> bool:
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO journal_metadata (emotion, severity, cause, content, word_count, doc_url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (emotion, severity, cause, content, word_count, doc_url, timestamp)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving journal metadata: {e}")
        return False

def get_journal_history() -> list:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT emotion, severity, cause, content, word_count, doc_url, timestamp FROM journal_metadata ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()
        
        # Convert list of rows to list of dicts matching original JSON structure
        entries = []
        for row in rows:
            entries.append({
                "timestamp": row["timestamp"],
                "content": row["content"],
                "emotion": row["emotion"],
                "severity": row["severity"],
                "cause": row["cause"],
                "word_count": row["word_count"],
                "doc_url": row["doc_url"]
            })
        return entries
    except Exception as e:
        print(f"Error getting journal history: {e}")
        return []

# --- Reminders Operations ---

def get_reminders() -> list:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, activity, time, frequency, active, timestamp FROM reminders ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        conn.close()
        
        reminders = []
        for row in rows:
            reminders.append({
                "id": row["id"],
                "activity": row["activity"],
                "time": row["time"],
                "frequency": row["frequency"],
                "active": bool(row["active"]),
                "timestamp": row["timestamp"]
            })
        return reminders
    except Exception as e:
        print(f"Error getting reminders: {e}")
        return []

def create_reminder(reminder_id: str, activity: str, time: str, frequency: str, active: bool = True, timestamp: str = None) -> bool:
    if not timestamp:
        timestamp = datetime.now().isoformat()
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reminders (id, activity, time, frequency, active, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (reminder_id, activity, time, frequency, 1 if active else 0, timestamp)
        )
        # Log to reminder_history
        cursor.execute(
            """
            INSERT INTO reminder_history (reminder_id, activity, action, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (reminder_id, activity, "created", timestamp)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating reminder: {e}")
        return False

def toggle_reminder(reminder_id: str) -> dict:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get current reminder info
        cursor.execute("SELECT activity, active FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": "Reminder not found"}
        
        activity = row["activity"]
        new_active_val = 0 if row["active"] else 1
        timestamp = datetime.now().isoformat()
        
        # Update active state
        cursor.execute("UPDATE reminders SET active = ? WHERE id = ?", (new_active_val, reminder_id))
        
        # Log action to history
        cursor.execute(
            """
            INSERT INTO reminder_history (reminder_id, activity, action, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (reminder_id, activity, "toggled", timestamp)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Reminder state toggled successfully."}
    except Exception as e:
        print(f"Error toggling reminder: {e}")
        return {"status": "error", "message": str(e)}

def delete_reminder(reminder_id: str) -> dict:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get reminder activity to log
        cursor.execute("SELECT activity FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"status": "error", "message": "Reminder not found"}
            
        activity = row["activity"]
        timestamp = datetime.now().isoformat()
        
        # Delete reminder
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        
        # Log action to history
        cursor.execute(
            """
            INSERT INTO reminder_history (reminder_id, activity, action, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (reminder_id, activity, "deleted", timestamp)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Reminder deleted successfully."}
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return {"status": "error", "message": str(e)}
