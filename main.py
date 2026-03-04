import tkinter as tk

from gui import AttendanceGUI


def main():
    root = tk.Tk()
    AttendanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
