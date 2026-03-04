# Smart Face Attendance System

Real-time face recognition attendance system with a professional Tkinter desktop interface.

## Features
- Live camera feed with multi-face recognition
- TensorFlow Lite FaceNet inference
- Cosine similarity matching against local gallery
- Confirmation window (`required_frames`) to reduce false positives
- Automatic CSV attendance logging per day
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
├── core/
│   ├── __init__.py
│   ├── attendance.py
│   ├── config.py
│   └── recognition.py
├── ui/
│   ├── __init__.py
│   ├── layout.py
│   └── theme.py
└── data/
    └── attendance_logs/
```

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Configuration
Adjust runtime settings in `core/config.py`:
- model/gallery/names paths
- camera index
- recognition thresholds
- UI refresh intervals

## Recognition Pipeline
1. Detect faces with Haar Cascade.
2. Preprocess to FaceNet input format.
3. Infer embedding with TFLite interpreter.
4. Compare embedding with stored gallery via cosine similarity.
5. Mark `PRESENT` after stable confirmation frames.

## Notes
- Daily attendance files are saved as `data/attendance_logs/YYYY-MM-DD.csv`.
- `gallery.npy` and `names.txt` must align by index.
