# Smart Face Attendance System

Real-time face recognition attendance system with a professional Tkinter desktop interface.

## Features
- Live camera feed with multi-face recognition
- TensorFlow Lite FaceNet inference
- Cosine similarity matching against local gallery
- Confirmation window (`required_frames`) to reduce false positives
- SQLite-backed attendance storage per day
- Dashboard view for total/present/absent and live check-ins

## Project Structure
```text
Smart-Face-Attendance-System/
├── main.py
├── gui.py
├── requirements.txt
├── README.md
├── .gitignore
├── model_int8.tflite
├── gallery.npy
├── names.txt
├── logs/
├── data/
│   ├── attendance.db
│   └── attendance_logs/
├── core/
│   ├── __init__.py
│   ├── attendance.py
│   ├── config.py
│   ├── database.py
│   ├── logging_config.py
│   └── recognition.py
├── ui/
│   ├── __init__.py
│   ├── layout.py
│   └── theme.py
└── tests/
```

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Logging
- App logs are written to `logs/app.log`.
- Logging is initialized in `main.py` via `core/logging_config.py`.
- File logs are rotated automatically (default: 1 MB per file, 5 backups).

## Configuration
Adjust runtime settings in `core/config.py`:
- model/gallery/names paths
- camera index
- recognition thresholds
- UI refresh intervals
- SQLite database path

## Recognition Pipeline
1. Detect faces with Haar Cascade.
2. Preprocess to FaceNet input format.
3. Infer embedding with TFLite interpreter.
4. Compare embedding with stored gallery via cosine similarity.
5. Mark `PRESENT` after stable confirmation frames.

## Notes
- Attendance is stored in `data/attendance.db`.
- `data/attendance_logs/` is retained for backward compatibility and optional exports.
- `gallery.npy` and `names.txt` must align by index.

## One-Time Migration (CSV -> SQLite)
If you have legacy CSV logs in `data/attendance_logs/`, run:

```bash
python scripts/migrate_csv_to_sqlite.py
```

Optional paths:

```bash
python scripts/migrate_csv_to_sqlite.py --csv-dir data/attendance_logs --db-path data/attendance.db
```

## Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```
