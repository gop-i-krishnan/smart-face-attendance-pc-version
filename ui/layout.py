import tkinter as tk
from datetime import datetime
from tkinter import ttk

from ui.theme import COLORS, FONT_BODY, FONT_BODY_BOLD, FONT_H2, FONT_TITLE


def configure_treeview_style() -> None:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=COLORS["card"],
        fieldbackground=COLORS["card"],
        foreground=COLORS["text"],
        rowheight=30,
        font=FONT_BODY,
    )
    style.configure(
        "Treeview.Heading",
        background="#ECFEFF",
        foreground=COLORS["primary_dark"],
        font=("Segoe UI Semibold", 10),
        relief="flat",
    )
    style.map("Treeview", background=[("selected", "#CCFBF1")])


def build_main_layout(root: tk.Tk, on_start, on_stop) -> dict[str, object]:
    root.configure(bg=COLORS["bg"])
    root.geometry("1120x760")
    root.minsize(980, 700)

    widgets: dict[str, object] = {}

    main = tk.Frame(root, bg=COLORS["bg"])
    main.pack(fill="both", expand=True, padx=20, pady=16)

    header = tk.Frame(
        main,
        bg=COLORS["card"],
        highlightthickness=1,
        highlightbackground=COLORS["line"],
    )
    header.pack(fill="x", pady=(0, 14))

    tk.Label(
        header,
        text="Smart Face Attendance",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_TITLE,
    ).grid(row=0, column=0, padx=18, pady=(14, 0), sticky="w")

    tk.Label(
        header,
        text="Real-time recognition and automated logging",
        bg=COLORS["card"],
        fg=COLORS["muted"],
        font=("Segoe UI", 11),
    ).grid(row=1, column=0, padx=18, pady=(2, 14), sticky="w")

    clock_label = tk.Label(
        header,
        text="--:--:--",
        bg=COLORS["card"],
        fg=COLORS["primary_dark"],
        font=("Consolas", 14, "bold"),
    )
    clock_label.grid(row=0, column=1, padx=18, pady=14, sticky="e")
    header.grid_columnconfigure(0, weight=1)

    content = tk.Frame(main, bg=COLORS["bg"])
    content.pack(fill="both", expand=True)
    content.grid_columnconfigure(0, weight=3)
    content.grid_columnconfigure(1, weight=2)
    content.grid_rowconfigure(0, weight=1)

    video_card = tk.Frame(
        content,
        bg=COLORS["card"],
        highlightthickness=1,
        highlightbackground=COLORS["line"],
    )
    video_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

    tk.Label(
        video_card,
        text="Live Camera Feed",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_H2,
    ).pack(anchor="w", padx=14, pady=(12, 8))

    video_label = tk.Label(video_card, bg="#D1D5DB", width=78, height=28)
    video_label.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    side = tk.Frame(content, bg=COLORS["bg"])
    side.grid(row=0, column=1, sticky="nsew")

    control_card = tk.Frame(
        side,
        bg=COLORS["card"],
        highlightthickness=1,
        highlightbackground=COLORS["line"],
    )
    control_card.pack(fill="x", pady=(0, 10))

    tk.Label(
        control_card,
        text="Controls",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_H2,
    ).pack(anchor="w", padx=14, pady=(12, 10))

    button_row = tk.Frame(control_card, bg=COLORS["card"])
    button_row.pack(fill="x", padx=14, pady=(0, 10))

    start_button = tk.Button(
        button_row,
        text="Start Camera",
        command=on_start,
        bg=COLORS["primary"],
        activebackground=COLORS["primary_dark"],
        fg="white",
        activeforeground="white",
        relief="flat",
        font=("Segoe UI Semibold", 10),
        padx=12,
        pady=8,
        cursor="hand2",
    )
    start_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

    stop_button = tk.Button(
        button_row,
        text="Stop Camera",
        command=on_stop,
        bg=COLORS["danger"],
        activebackground=COLORS["danger_dark"],
        fg="white",
        activeforeground="white",
        relief="flat",
        font=("Segoe UI Semibold", 10),
        padx=12,
        pady=8,
        cursor="hand2",
        state=tk.DISABLED,
    )
    stop_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

    status_label = tk.Label(
        control_card,
        text="System Idle",
        bg="#ECFEFF",
        fg=COLORS["primary_dark"],
        font=FONT_BODY_BOLD,
        padx=10,
        pady=7,
    )
    status_label.pack(anchor="w", padx=14, pady=(0, 12))

    stats_card = tk.Frame(
        side,
        bg=COLORS["card"],
        highlightthickness=1,
        highlightbackground=COLORS["line"],
    )
    stats_card.pack(fill="x", pady=(0, 10))

    tk.Label(
        stats_card,
        text="Attendance Stats",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_H2,
    ).pack(anchor="w", padx=14, pady=(12, 8))

    total_label = tk.Label(
        stats_card, text="", bg=COLORS["card"], fg=COLORS["muted"], font=FONT_BODY
    )
    total_label.pack(anchor="w", padx=14)

    present_label = tk.Label(
        stats_card,
        text="",
        bg=COLORS["card"],
        fg=COLORS["primary_dark"],
        font=("Segoe UI Semibold", 10),
    )
    present_label.pack(anchor="w", padx=14, pady=(4, 0))

    absent_label = tk.Label(
        stats_card,
        text="",
        bg=COLORS["card"],
        fg=COLORS["accent"],
        font=("Segoe UI Semibold", 10),
    )
    absent_label.pack(anchor="w", padx=14, pady=(4, 12))

    table_card = tk.Frame(
        side,
        bg=COLORS["card"],
        highlightthickness=1,
        highlightbackground=COLORS["line"],
    )
    table_card.pack(fill="both", expand=True)

    tk.Label(
        table_card,
        text="Today's Check-ins",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=FONT_H2,
    ).pack(anchor="w", padx=14, pady=(12, 8))

    date_label = tk.Label(
        table_card,
        text=f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        bg=COLORS["card"],
        fg=COLORS["muted"],
        font=FONT_BODY,
    )
    date_label.pack(anchor="w", padx=14, pady=(0, 8))

    table_wrap = tk.Frame(table_card, bg=COLORS["card"])
    table_wrap.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    table = ttk.Treeview(table_wrap, columns=("Name", "Time"), show="headings")
    table.heading("Name", text="Name")
    table.heading("Time", text="Time")
    table.column("Name", width=150, anchor="center")
    table.column("Time", width=120, anchor="center")

    y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=y_scroll.set)
    table.pack(side="left", fill="both", expand=True)
    y_scroll.pack(side="right", fill="y")

    widgets["clock_label"] = clock_label
    widgets["video_label"] = video_label
    widgets["start_button"] = start_button
    widgets["stop_button"] = stop_button
    widgets["status_label"] = status_label
    widgets["total_label"] = total_label
    widgets["present_label"] = present_label
    widgets["absent_label"] = absent_label
    widgets["date_label"] = date_label
    widgets["table"] = table
    return widgets
