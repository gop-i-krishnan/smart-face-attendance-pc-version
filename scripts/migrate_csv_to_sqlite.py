import argparse
import csv
import sys
from pathlib import Path

# Allow direct script execution: `python scripts/migrate_csv_to_sqlite.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.database import AttendanceRepository


def migrate(csv_dir: Path, db_path: Path) -> tuple[int, int, int]:
    repo = AttendanceRepository(db_path)

    imported = 0
    skipped_duplicates = 0
    skipped_invalid = 0

    csv_files = sorted(csv_dir.glob("*.csv"))
    for csv_file in csv_files:
        fallback_date = csv_file.stem
        with csv_file.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = (row.get("Name") or "").strip()
                date = (row.get("Date") or fallback_date).strip()
                time = (row.get("Time") or "").strip()

                if not name or not date or not time:
                    skipped_invalid += 1
                    continue

                created_at = f"{date}T{time}"
                inserted = repo.upsert_attendance(
                    name=name,
                    on_date=date,
                    at_time=time,
                    created_at=created_at,
                )
                if inserted:
                    imported += 1
                else:
                    skipped_duplicates += 1

    return imported, skipped_duplicates, skipped_invalid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-time migration: CSV attendance logs -> SQLite database."
    )
    parser.add_argument(
        "--csv-dir",
        default="data/attendance_logs",
        help="Directory containing legacy attendance CSV files.",
    )
    parser.add_argument(
        "--db-path",
        default="data/attendance.db",
        help="Target SQLite database path.",
    )
    args = parser.parse_args()

    csv_dir = Path(args.csv_dir)
    db_path = Path(args.db_path)

    if not csv_dir.exists():
        raise SystemExit(f"CSV directory not found: {csv_dir}")

    imported, skipped_duplicates, skipped_invalid = migrate(csv_dir, db_path)
    print(f"Migration complete -> DB: {db_path}")
    print(f"Imported rows: {imported}")
    print(f"Skipped duplicates: {skipped_duplicates}")
    print(f"Skipped invalid rows: {skipped_invalid}")


if __name__ == "__main__":
    main()
