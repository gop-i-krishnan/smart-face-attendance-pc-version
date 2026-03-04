import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from core.attendance import AttendanceManager


class TestAttendanceManager(unittest.TestCase):
    def test_initializes_database_and_syncs_students(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = AttendanceManager(
                ["Alice", "Bob"],
                Path(tmp_dir) / "attendance_logs",
                Path(tmp_dir) / "attendance.db",
            )
            self.assertTrue((Path(tmp_dir) / "attendance.db").exists())
            self.assertEqual(manager.get_total_students(), 2)

    def test_mark_present_once_per_name_per_day(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = AttendanceManager(
                ["Alice"],
                Path(tmp_dir) / "attendance_logs",
                Path(tmp_dir) / "attendance.db",
            )
            today = datetime.now().strftime("%Y-%m-%d")
            manager.mark_present("Alice")
            manager.mark_present("Alice")

            rows = manager.get_rows_for_date(today)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], "Alice")
            self.assertEqual(manager.get_present_count_for_date(today), 1)


if __name__ == "__main__":
    unittest.main()
