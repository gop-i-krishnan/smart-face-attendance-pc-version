import logging
from datetime import datetime

import cv2
from PIL import Image, ImageTk

from core.attendance import AttendanceManager
from core.config import AppConfig, RecognitionConfig
from core.recognition import FaceRecognitionEngine
from ui.layout import build_main_layout, configure_treeview_style
from ui.theme import COLORS

logger = logging.getLogger(__name__)


class AttendanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Face Attendance System")

        self.app_config = AppConfig()
        self.recognition_config = RecognitionConfig()
        self.engine = FaceRecognitionEngine(self.app_config, self.recognition_config)
        self.attendance_manager = AttendanceManager(
            self.engine.names,
            self.app_config.attendance_dir,
            self.app_config.database_path,
        )

        self.is_running = False
        self.cap = None

        configure_treeview_style()
        self.widgets = build_main_layout(root, self.start_system, self.stop_system)

        self.refresh_table()
        self.update_clock()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        logger.info("GUI initialized with %d registered identities", len(self.engine.names))

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
            logger.error("Camera not found at index %d", self.app_config.camera_index)
            return

        self.is_running = True
        self.widgets["start_button"].config(state="disabled")
        self.widgets["stop_button"].config(state="normal")
        self.set_status("Camera Running", "info")
        logger.info("Camera started at index %d", self.app_config.camera_index)
        self.update_frame()

    def stop_system(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

        self.is_running = False
        self.widgets["start_button"].config(state="normal")
        self.widgets["stop_button"].config(state="disabled")
        self.set_status("System Stopped", "error")
        logger.info("Camera stopped")

    def update_frame(self) -> None:
        if not (self.is_running and self.cap):
            return

        ret, frame = self.cap.read()
        if ret:
            frame, newly_marked = self.engine.process_frame(frame)
            for name in newly_marked:
                self.attendance_manager.mark_present(name)
                self.set_status(f"Marked PRESENT: {name}", "success")
                logger.info("Recognition confirmed for %s", name)

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
        rows = self.attendance_manager.get_rows_for_date(today)
        for row in rows:
            table.insert("", "end", values=(row[0], row[1]))

        present_count = self.attendance_manager.get_present_count_for_date(today)
        total = self.attendance_manager.get_total_students()
        absent = max(total - present_count, 0)
        self.widgets["total_label"].config(text=f"Total Registered: {total}")
        self.widgets["present_label"].config(text=f"Present Today: {present_count}")
        self.widgets["absent_label"].config(text=f"Absent Today: {absent}")
        self.widgets["date_label"].config(text=f"Date: {today}")

        self.root.after(self.app_config.table_refresh_ms, self.refresh_table)

    def on_close(self) -> None:
        logger.info("Application closing")
        self.stop_system()
        self.root.destroy()
