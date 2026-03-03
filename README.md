# Smart Face Attendance System (PC Version)

## Overview

Smart Face Attendance System is a real-time face recognition-based attendance application built using FaceNet (512-dimensional embeddings) and TensorFlow Lite.

The system captures live video from a webcam, detects faces, generates embeddings using a pre-trained FaceNet model, compares them with a stored gallery using cosine similarity, and marks attendance automatically.

This version is fully software-based and runs entirely on a PC (no FPGA required).

---

## Key Features

- Real-time face detection using OpenCV
- FaceNet model (InceptionResNetV2 backbone)
- 512-dimensional L2-normalized embeddings
- Cosine similarity-based recognition
- Multi-face recognition support
- Confidence threshold filtering (default: 0.60)
- 15-frame confirmation logic for stability
- Live bounding boxes and confidence display
- Attendance status overlay
- TensorFlow Lite inference (Float32 model)

---

## System Architecture


    Webcam
      ↓
    Face Detection (Haar Cascade)
      ↓
    Preprocessing (Resize 160×160, Normalize to [-1, 1])
      ↓
    TFLite FaceNet Inference
      ↓
    512-D Embedding
      ↓
    Cosine Similarity with Gallery
      ↓
    Threshold Check
      ↓
    Attendance Marking


---

## Model Details

- Model: FaceNet (Pre-trained)
- Backbone: InceptionResNetV2
- Input Shape: 160 × 160 × 3 (RGB)
- Output: 512-dimensional embedding
- Similarity Metric: Cosine Similarity
- Threshold: 0.60
- Frame Confirmation Requirement: 15 frames

---

## Performance (PC)

- Frame Rate: 30–60 FPS
- Latency: ~20 ms per frame
- Multi-face recognition supported
- Robust under moderate lighting variation

---

## Project Structure


    Smart-Face-Attendance-System/
    │
    ├── main.py
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    │
    ├── model_dynamic.tflite
    ├── gallery.npy
    └── names.txt


---

## Installation

1. Clone the repository:


git clone [https://github.com/gop-i-krishnan/Smart-Face-Attendance-System.git](https://github.com/gop-i-krishnan/smart-face-attendance-pc-version.git)

cd Smart-Face-Attendance-System


2. Install dependencies:


pip install -r requirements.txt


---

## How to Run


python main.py


- Press `q` to quit the application.
- Recognized individuals will be marked as PRESENT after 15 confirmed frames.

---

## Gallery Database

The system uses:

- `gallery.npy` → 512-dimensional embeddings per person  
- `names.txt` → Corresponding names  

Each embedding is L2-normalized for stable cosine similarity comparison.

---

## Recognition Logic

1. Extract embedding from detected face
2. Normalize embedding
3. Compute cosine similarity with stored gallery
4. Select highest similarity score
5. If score > threshold → Mark as recognized
6. If confirmed for 15 frames → Mark attendance

---

## Future Improvements

- Replace Haar Cascade with MediaPipe for better detection
- Add GUI interface (Tkinter / PyQt)
- Add dynamic enrollment feature
- Store attendance in SQLite database
- Add web dashboard
- Deploy as Docker container

---

## Author

Developed as part of a Smart Face Attendance System mini project.

Team Members:
- Gopi Krishnan
- Milan Martin
- Gilbert Franco

---

## License

This project is for educational and research purposes.
