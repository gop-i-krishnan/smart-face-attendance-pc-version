import cv2
import time
import numpy as np
import tensorflow as tf
from collections import defaultdict

from core.attendance import AttendanceManager


# ================= CONFIG =================
IMG_SIZE = (160, 160)
MODEL_PATH = "model_int8.tflite"
SIM_THRESHOLD = 0.60
MARGIN = 0.08
REQUIRED_FRAMES = 15
GALLERY_PATH = "gallery.npy"
NAMES_PATH = "names.txt"

# ================= LOAD DATA =================
gallery = np.load(GALLERY_PATH).astype(np.float32)
gallery = gallery / (np.linalg.norm(gallery, axis=1, keepdims=True) + 1e-10)

with open(NAMES_PATH, "r") as f:
    names = [line.strip() for line in f.readlines()]

attendance_manager = AttendanceManager(names)

attendance = {name: "ABSENT" for name in names}
frame_count = defaultdict(int)
last_seen = {}
TIMEOUT_SECONDS = 3

print(f"✅ Loaded {len(names)} people from gallery")
print(f"   Names: {names}")

# ================= LOAD MODEL =================
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()[0]
output_details = interpreter.get_output_details()[0]

print(f"✅ Model loaded: {MODEL_PATH}")
print(f"   Input shape: {input_details['shape']}")
print(f"   Output shape: {output_details['shape']}")

# ================= FACE DETECTOR =================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ================= CAMERA =================
cap = cv2.VideoCapture(0)
print("\n🎥 Camera started. Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        cv2.imshow("Face Attendance Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # 🔴 PROCESS ALL FACES (not just the largest one)
    for (x, y, w, h) in faces:
        # Add margin
        mh = int(h * MARGIN)
        mw = int(w * MARGIN)
        y1 = max(0, y - mh)
        y2 = min(frame.shape[0], y + h + mh)
        x1 = max(0, x - mw)
        x2 = min(frame.shape[1], x + w + mw)

        face = frame[y1:y2, x1:x2]

        # Preprocess face
        img = cv2.resize(face, IMG_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32)
        
        # FaceNet preprocessing
        img = (img - 127.5) / 128.0
        
        inp = np.expand_dims(img, axis=0)

        # Handle int8 quantization if needed
        if input_details["dtype"] == np.int8:
            scale, zero = input_details["quantization"]
            inp = np.round(inp / scale + zero).astype(np.int8)
            inp = np.clip(inp, -128, 127)

        # Run inference
        interpreter.set_tensor(input_details["index"], inp)
        interpreter.invoke()
        emb = interpreter.get_tensor(output_details["index"]).squeeze()

        # Handle int8 output
        if output_details["dtype"] == np.int8:
            scale, zero = output_details["quantization"]
            emb = (emb.astype(np.float32) - zero) * scale

        # Normalize embedding
        emb = emb / (np.linalg.norm(emb) + 1e-10)

        # Calculate similarities
        sims = gallery @ emb
        best_idx = np.argmax(sims)
        best_score = sims[best_idx]

        # Recognition logic
        if best_score > SIM_THRESHOLD:
            name = names[best_idx]
            current_time = time.time()

            # Reset frame count if timeout exceeded
            if name in last_seen:
                if current_time - last_seen[name] > TIMEOUT_SECONDS:
                    frame_count[name] = 0

            frame_count[name] += 1
            last_seen[name] = current_time
            
            if frame_count[name] >= REQUIRED_FRAMES:
                if attendance[name] != "PRESENT":
                    attendance[name] = "PRESENT"
                    attendance_manager.mark_present(name)
            
            label = f"{name} ({best_score:.2f})"
            color = (0, 255, 0)
        else:
            label = f"Unknown ({best_score:.2f})"
            color = (0, 0, 255)

        # Draw rectangle and label for THIS face
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Draw attendance status (bottom left)
    y0 = frame.shape[0] - 100
    for person, status in attendance.items():
        status_color = (0, 255, 0) if status == "PRESENT" else (255, 255, 0)
        cv2.putText(frame, f"{person}: {status}",
                    (20, y0),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    status_color,
                    2)
        y0 += 25

    cv2.imshow("Face Attendance Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
exit(0)
