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
        self.process = None
        self.cap = None
        
        # Load FaceNet model
        self.interpreter = tf.lite.Interpreter(model_path="model_int8.tflite")
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]
        
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
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (500, 350))

                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)

                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)

            self.root.after(30, self.update_frame)
        
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