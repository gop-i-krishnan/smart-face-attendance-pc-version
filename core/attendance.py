import os
import csv
from datetime import datetime

class AttendanceManager:
    def __init__(self, names):
        self.names = names
        self.present_today = set()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.file_path = f"data/attendance_logs/{self.today}.csv"

        os.makedirs("data/attendance_logs", exist_ok=True)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time"])

    def mark_present(self, name):
        if name in self.present_today:
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        with open(self.file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, date, time])

        self.present_today.add(name)