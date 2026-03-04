import csv
from datetime import datetime

import cv2
from PIL import Image, ImageTk

from core.attendance import AttendanceManager
from core.config import AppConfig, RecognitionConfig
from core.recognition import FaceRecognitionEngine
from ui.layout import build_main_layout, configure_treeview_style
from ui.theme import COLORS


class AttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Face Attendance System")

        self.app_config = AppConfig()
        self.recognition_config = RecognitionConfig()
        self.engine = FaceRecognitionEngine(self.app_config, self.recognition_config)
        self.attendance_manager = AttendanceManager(
            self.engine.names, self.app_config.attendance_dir
        )

        self.is_running = False
        self.cap = None

        configure_treeview_style()
        self.widgets = build_main_layout(root, self.start_system, self.stop_system)

        self.refresh_table()
        self.update_clock()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_status(self, text: str, mode: str = "info") -> None:
        palette = {
            "info": ("#ECFEFF", COLORS["primary_dark"]),
            "success": ("#DCFCE7", "#166534"),
            "error": ("#FEE2E2", "#991B1B"),
        }
        bg, fg = palette.get(mode, palette["info"])
        self.widgets["status_label"].config(text=text, bg=bg, fg=fg)

    def update_clock(self) -> None:
        now = datetime.now()
        self.widgets["clock_label"].config(text=now.strftime("%H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def start_system(self) -> None:
        if self.is_running:
            return

        self.cap = cv2.VideoCapture(self.app_config.camera_index)
        if not self.cap.isOpened():
            self.set_status("Camera not found", "error")
            return

        self.is_running = True
        self.widgets["start_button"].config(state="disabled")
        self.widgets["stop_button"].config(state="normal")
        self.set_status("Camera Running", "info")
        self.update_frame()

    def stop_system(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

        self.is_running = False
        self.widgets["start_button"].config(state="normal")
        self.widgets["stop_button"].config(state="disabled")
        self.set_status("System Stopped", "error")

    def update_frame(self) -> None:
        if not (self.is_running and self.cap):
            return

        ret, frame = self.cap.read()
        if ret:
            frame, newly_marked = self.engine.process_frame(frame)
            for name in newly_marked:
                self.attendance_manager.mark_present(name)
                self.set_status(f"Marked PRESENT: {name}", "success")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (680, 420))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.widgets["video_label"].imgtk = imgtk
            self.widgets["video_label"].configure(image=imgtk)

        self.root.after(self.app_config.frame_delay_ms, self.update_frame)

    def refresh_table(self) -> None:
        table = self.widgets["table"]
        table.delete(*table.get_children())

        today = datetime.now().strftime("%Y-%m-%d")
        file_path = self.app_config.attendance_dir / f"{today}.csv"
        present_count = 0

        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    table.insert("", "end", values=(row[0], row[2]))
                    present_count += 1

        total = len(self.engine.names)
        absent = max(total - present_count, 0)
        self.widgets["total_label"].config(text=f"Total Registered: {total}")
        self.widgets["present_label"].config(text=f"Present Today: {present_count}")
        self.widgets["absent_label"].config(text=f"Absent Today: {absent}")
        self.widgets["date_label"].config(text=f"Date: {today}")

        self.root.after(self.app_config.table_refresh_ms, self.refresh_table)

    def on_close(self) -> None:
        self.stop_system()
        self.root.destroy()
