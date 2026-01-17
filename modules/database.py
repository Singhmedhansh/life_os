import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "life_os.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


# --- Connection helpers ---

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            task_name TEXT NOT NULL,
            category TEXT NOT NULL,
            status INTEGER DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS finance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            note TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            habit TEXT NOT NULL,
            status INTEGER DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS timer_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            subject TEXT DEFAULT 'General'
        )
        """
    )
    conn.commit()
    conn.close()


# --- Tasks (Academics / Health) ---

def upsert_task(date_str: str, task_name: str, category: str, status: int = 0) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM tasks WHERE date=? AND task_name=? AND category=?",
        (date_str, task_name, category),
    )
    row = cur.fetchone()
    if row:
        # Existing task: keep current status to avoid resetting completed items on rerender
        conn.close()
        return
    else:
        cur.execute(
            "INSERT INTO tasks (date, task_name, category, status) VALUES (?, ?, ?, ?)",
            (date_str, task_name, category, status),
        )
    conn.commit()
    conn.close()


def set_task_status(date_str: str, task_name: str, category: str, status: bool) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET status=? WHERE date=? AND task_name=? AND category=?",
        (1 if status else 0, date_str, task_name, category),
    )
    conn.commit()
    conn.close()


def get_tasks(date_str: str, category: Optional[str] = None) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    if category:
        cur.execute(
            "SELECT * FROM tasks WHERE date=? AND category=? ORDER BY id ASC",
            (date_str, category),
        )
    else:
        cur.execute(
            "SELECT * FROM tasks WHERE date=? ORDER BY id ASC",
            (date_str,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def add_custom_task(date_str: str, task_name: str, category: str = "Academics") -> None:
    upsert_task(date_str, task_name, category, status=0)


# --- Finance ---

def add_finance_entry(date_str: str, category: str, amount: float, note: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO finance (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date_str, category, amount, note),
    )
    conn.commit()
    conn.close()


def get_finance(limit: int = 100) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM finance ORDER BY date ASC, id ASC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_recent_finance(limit: int = 5) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM finance ORDER BY date DESC, id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


# --- Habits ---

def upsert_habit(date_str: str, habit: str, status: int = 0) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM habits WHERE date=? AND habit=?",
        (date_str, habit),
    )
    row = cur.fetchone()
    if row:
        conn.close()
        return
    else:
        cur.execute(
            "INSERT INTO habits (date, habit, status) VALUES (?, ?, ?)",
            (date_str, habit, status),
        )
    conn.commit()
    conn.close()


def set_habit_status(date_str: str, habit: str, status: bool) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE habits SET status=? WHERE date=? AND habit=?",
        (1 if status else 0, date_str, habit),
    )
    conn.commit()
    conn.close()


def get_habits(date_str: str) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM habits WHERE date=? ORDER BY id ASC",
        (date_str,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_habit_streak(habit: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, status FROM habits WHERE habit=? ORDER BY date DESC, id DESC",
        (habit,),
    )
    rows = cur.fetchall()
    conn.close()
    streak = 0
    last_date = None
    for r in rows:
        if not r["status"]:
            break
        streak += 1
    return streak

# --- Timer Sessions ---

def add_timer_session(date_str: str, start_time: str, duration_minutes: int, subject: str = "General", completed: int = 1) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO timer_sessions (date, start_time, duration_minutes, completed, subject) VALUES (?, ?, ?, ?, ?)",
        (date_str, start_time, duration_minutes, completed, subject),
    )
    conn.commit()
    conn.close()


def get_timer_sessions(date_str: str) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM timer_sessions WHERE date=? ORDER BY start_time DESC",
        (date_str,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_timer_stats(date_str: str) -> Dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT SUM(duration_minutes) as total_minutes, COUNT(*) as total_sessions, SUM(completed) as completed_sessions FROM timer_sessions WHERE date=?",
        (date_str,),
    )
    row = cur.fetchone()
    conn.close()
    
    return {
        "total_minutes": row["total_minutes"] or 0,
        "total_sessions": row["total_sessions"] or 0,
        "completed_sessions": row["completed_sessions"] or 0,
    }


def get_focus_streak() -> int:
    """Get days in a row with at least one completed focus session"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT date FROM timer_sessions WHERE completed=1 ORDER BY date DESC",
    )
    rows = cur.fetchall()
    conn.close()
    
    from datetime import date, timedelta
    streak = 0
    current_date = date.today()
    
    for row in rows:
        session_date = date.fromisoformat(row["date"])
        if session_date == current_date:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak