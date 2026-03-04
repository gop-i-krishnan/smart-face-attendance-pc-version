import csv
from datetime import datetime
from pathlib import Path


class AttendanceManager:
    def __init__(self, names: list[str], attendance_dir: Path):
        self.names = names
        self.attendance_dir = attendance_dir
        self.present_today = set()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.file_path = self.attendance_dir / f"{self.today}.csv"

        self.attendance_dir.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            with self.file_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time"])

    def mark_present(self, name: str) -> None:
        if name in self.present_today:
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        with self.file_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, date, current_time])

        self.present_today.add(name)
