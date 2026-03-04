import tkinter as tk
from tkinter import ttk
import cv2
import time
import numpy as np
import tensorflow as tf
from PIL import Image, ImageTk
import os
import csv
from datetime import datetime
from collections import defaultdict

from core.attendance import AttendanceManager

class AttendanceGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Face Attendance System")
        self.root.geometry("700x650")

        self.is_running = False
        self.cap = None
        
        # Load FaceNet model
        self.interpreter = tf.lite.Interpreter(model_path="model_int8.tflite")
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        
        # Face recognition config
        self.IMG_SIZE = (160, 160)
        self.SIM_THRESHOLD = 0.60
        self.REQUIRED_FRAMES = 15
        self.MARGIN = 0.08

        self.gallery = np.load("gallery.npy").astype(np.float32)
        self.gallery = self.gallery / (np.linalg.norm(self.gallery, axis=1, keepdims=True) + 1e-10)

        with open("names.txt", "r") as f:
            self.names = [line.strip() for line in f.readlines()]

        self.attendance_manager = AttendanceManager(self.names)

        self.attendance = {name: "ABSENT" for name in self.names}
        self.frame_count = defaultdict(int)
        self.last_seen = {}
        self.TIMEOUT_SECONDS = 3

        title = tk.Label(root, text="Smart Face Attendance System",
                         font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.start_button = tk.Button(root, text="Start Camera",
                                      command=self.start_system,
                                      width=20, bg="green", fg="white")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Camera",
                                     command=self.stop_system,
                                     width=20, bg="red", fg="white",
                                     state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.status_label = tk.Label(root, text="System Idle",
                                     font=("Arial", 12))
        self.status_label.pack(pady=20)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.table = ttk.Treeview(root, columns=("Name", "Time"), show="headings")
        self.table.heading("Name", text="Name")
        self.table.heading("Time", text="Time")
        self.table.pack(pady=10, fill="both", expand=True)
        
        self.date_label = tk.Label(
            root,
            text=f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            font=("Arial", 11)
        )
        self.date_label.pack()
        
        self.table.column("Name", width=200, anchor="center")
        self.table.column("Time", width=150, anchor="center")
        
        self.refresh_table()
    
    def start_system(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.status_label.config(text="Camera not found")
                return
            
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Camera Running...")
            self.update_frame()

    def stop_system(self):
        if self.cap:
            self.cap.release()
            self.cap = None

        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="System Stopped")
        
    def update_frame(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()

            if ret:
                frame = self.process_frame(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (500, 350))

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            self.root.after(30, self.update_frame)

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            mh = int(h * self.MARGIN)
            mw = int(w * self.MARGIN)
            y1 = max(0, y - mh)
            y2 = min(frame.shape[0], y + h + mh)
            x1 = max(0, x - mw)
            x2 = min(frame.shape[1], x + w + mw)

            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                continue

            img = cv2.resize(face, self.IMG_SIZE)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = img.astype(np.float32)
            img = (img - 127.5) / 128.0
            inp = np.expand_dims(img, axis=0)

            if self.input_details["dtype"] == np.int8:
                scale, zero = self.input_details["quantization"]
                inp = np.round(inp / scale + zero).astype(np.int8)
                inp = np.clip(inp, -128, 127)

            self.interpreter.set_tensor(self.input_details["index"], inp)
            self.interpreter.invoke()
            emb = self.interpreter.get_tensor(self.output_details["index"]).squeeze()

            if self.output_details["dtype"] == np.int8:
                scale, zero = self.output_details["quantization"]
                emb = (emb.astype(np.float32) - zero) * scale

            emb = emb / (np.linalg.norm(emb) + 1e-10)
            sims = self.gallery @ emb
            best_idx = int(np.argmax(sims))
            best_score = float(sims[best_idx])

            if best_score > self.SIM_THRESHOLD:
                name = self.names[best_idx]
                current_time = time.time()

                if name in self.last_seen and (current_time - self.last_seen[name] > self.TIMEOUT_SECONDS):
                    self.frame_count[name] = 0

                self.frame_count[name] += 1
                self.last_seen[name] = current_time

                if self.frame_count[name] >= self.REQUIRED_FRAMES and self.attendance[name] != "PRESENT":
                    self.attendance[name] = "PRESENT"
                    self.attendance_manager.mark_present(name)
                    self.status_label.config(text=f"Marked PRESENT: {name}")

                label = f"{name} ({best_score:.2f})"
                color = (0, 255, 0)
            else:
                label = f"Unknown ({best_score:.2f})"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        y0 = frame.shape[0] - 100
        for person, status in self.attendance.items():
            status_color = (0, 255, 0) if status == "PRESENT" else (255, 255, 0)
            cv2.putText(
                frame,
                f"{person}: {status}",
                (20, y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                status_color,
                2,
            )
            y0 += 25

        return frame
        
    def on_close(self):
        if self.cap:
            self.cap.release()
        self.root.destroy()
        
    def refresh_table(self):
        self.table.delete(*self.table.get_children())

        today = datetime.now().strftime("%Y-%m-%d")
        file_path = f"data/attendance_logs/{today}.csv"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    self.table.insert("", "end", values=(row[0], row[2]))

        self.root.after(3000, self.refresh_table)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()
