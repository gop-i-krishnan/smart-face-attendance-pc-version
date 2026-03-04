import tkinter as tk

from core.logging_config import setup_logging
from gui import AttendanceGUI


def main():
    setup_logging()
    root = tk.Tk()
    AttendanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
