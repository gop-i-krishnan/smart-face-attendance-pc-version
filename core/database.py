import sqlite3
from datetime import datetime
from pathlib import Path


class AttendanceRepository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(student_id, date),
                    FOREIGN KEY(student_id) REFERENCES students(id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_attendance_student ON attendance(student_id)"
            )

    def sync_students(self, names: list[str]) -> None:
        with self._connect() as conn:
            for name in names:
                conn.execute(
                    "INSERT OR IGNORE INTO students(name) VALUES (?)",
                    (name,),
                )

    def get_total_students(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM students").fetchone()
        return int(row[0] if row else 0)

    def mark_present(self, name: str, on_date: str | None = None) -> bool:
        today = on_date or datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        now_ts = datetime.now().isoformat(timespec="seconds")
        return self.upsert_attendance(name=name, on_date=today, at_time=now_time, created_at=now_ts)

    def upsert_attendance(
        self,
        name: str,
        on_date: str,
        at_time: str,
        created_at: str | None = None,
    ) -> bool:
        created_ts = created_at or datetime.now().isoformat(timespec="seconds")

        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO students(name) VALUES (?)", (name,))
            row = conn.execute(
                "SELECT id FROM students WHERE name = ?",
                (name,),
            ).fetchone()
            if row is None:
                return False
            student_id = int(row[0])
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO attendance(student_id, date, time, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (student_id, on_date, at_time, created_ts),
            )
            return cur.rowcount > 0

    def get_attendance_for_date(self, on_date: str) -> list[tuple[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT s.name, a.time
                FROM attendance a
                JOIN students s ON s.id = a.student_id
                WHERE a.date = ?
                ORDER BY a.time ASC
                """,
                (on_date,),
            ).fetchall()
        return [(str(row[0]), str(row[1])) for row in rows]

    def get_present_count_for_date(self, on_date: str) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE date = ?",
                (on_date,),
            ).fetchone()
        return int(row[0] if row else 0)
