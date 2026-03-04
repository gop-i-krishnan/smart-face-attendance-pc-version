import logging
from datetime import datetime
from pathlib import Path

from core.database import AttendanceRepository

logger = logging.getLogger(__name__)


class AttendanceManager:
    def __init__(self, names: list[str], attendance_dir: Path, database_path: Path):
        self.names = names
        self.attendance_dir = attendance_dir
        self.database_path = database_path

        self.repo = AttendanceRepository(database_path)
        self.repo.sync_students(names)
        logger.info("Database initialized at %s", self.database_path)

    def mark_present(self, name: str) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        inserted = self.repo.mark_present(name, today)
        if inserted:
            logger.info("Attendance marked present for %s", name)
        else:
            logger.info("Attendance already present for %s on %s", name, today)

    def get_rows_for_date(self, on_date: str) -> list[tuple[str, str]]:
        return self.repo.get_attendance_for_date(on_date)

    def get_present_count_for_date(self, on_date: str) -> int:
        return self.repo.get_present_count_for_date(on_date)

    def get_total_students(self) -> int:
        return self.repo.get_total_students()
