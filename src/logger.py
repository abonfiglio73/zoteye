from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING
import os
import tkinter as tk

if TYPE_CHECKING:
    from main import ZotEyeApp


class LogLevel(Enum):
    INFO = ("📌", None)
    SUCCESS = ("✅", None)
    WARNING = ("⚠️", None)
    ERROR = ("❌", None)
    STOP = ("🟥", None)
    SAVE = ("💾", None)
    FOLDER = ("📂", None)
    RUN = ("▶️", None)
    WORKING = ("⛏️", None)
    OPEN = ("🌐", None)
    ELABORATE = ("💻", None)
    STATISTICS = ("📊", None)

    @property
    def icon(self):
        return self.value[0]

    @property
    def color(self):
        return self.value[1]


class Logger:
    def __init__(self, app: ZotEyeApp):
        self.app = app
        self._progress_active = False
        self._link_id = 0

    def log(
        self,
        text: str,
        level: LogLevel | None = None,
        pdf_path: str | None = None,
    ):
        widget = self.app.log_text
        widget.config(state="normal")

        # Close active progress bar
        if self._progress_active:
            widget.insert(tk.END, "\n")
            self._progress_active = False

        # Icon
        if level is not None:
            icon_tag = f"icon_{widget.index('end')}"
            widget.insert(tk.END, level.icon + " ", icon_tag)

            if level.color:
                widget.tag_config(icon_tag, foreground=level.color)

        # Text
        if pdf_path:
            self._insert_text_with_links(widget, text, pdf_path)
        else:
            widget.insert(tk.END, text)

        widget.insert(tk.END, "\n")
        widget.see(tk.END)
        widget.config(state="disabled")

    def _insert_text_with_links(
        self,
        widget: tk.Text,
        text: str,
        pdf_path: str,
    ):
        pdf_name = os.path.basename(pdf_path)
        folder_path = os.path.dirname(pdf_path)

        clean_text = (
            text.replace("{folder}", "").replace("{file}", "").replace("{filename}", "")
        )

        widget.insert(tk.END, clean_text)

        if "{folder}" in text:
            self._insert_link(widget, "📂 ", folder_path)

        if "{file}" in text:
            self._insert_link(widget, "📄 ", pdf_path)

        widget.insert(tk.END, pdf_name)

    def _insert_link(
        self,
        widget: tk.Text,
        icon: str,
        path: str,
    ):
        tag = f"link_tag_{self._link_id}"
        self._link_id += 1
        widget.insert(tk.END, icon, tag)

        widget.tag_config(tag, foreground="#005fb8")
        widget.tag_bind(tag, "<Button-1>", lambda e, p=path: os.startfile(p))
        widget.tag_bind(tag, "<Enter>", lambda e: widget.config(cursor="hand2"))
        widget.tag_bind(tag, "<Leave>", lambda e: widget.config(cursor=""))

    def progress(
        self,
        percent: int,
        current_size: int = 0,
        bar_length: int = 30,
    ):
        widget = self.app.log_text
        widget.config(state="normal")

        filled = int(bar_length * percent // 100)
        bar = "|" * filled + " " * (bar_length - filled)
        size_kb = current_size / 1024

        display = f"[{bar}] {percent}% ({size_kb:.1f} KB)"

        if not self._progress_active:
            # New row
            widget.insert(tk.END, display)
            self._progress_active = True
        else:
            # Update last row
            last_line = widget.index("end-1l linestart")
            widget.delete(last_line, "end-1l lineend")
            widget.insert(last_line, display)

        widget.see(tk.END)
        widget.config(state="disabled")

    def progress_done(self):
        if not self._progress_active:
            return

        widget = self.app.log_text
        widget.config(state="normal")
        widget.insert(tk.END, "\n")
        widget.config(state="disabled")
        self._progress_active = False
