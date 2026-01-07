from __future__ import annotations
from typing import TYPE_CHECKING
from functions import set_title_bar_dark, center_window
from config import ICO_PATH, APP_NAME, APP_VERSION, AUTHOR, PUBLICATION_YEAR
import tkinter as tk
import tkinter.ttk as ttk


if TYPE_CHECKING:
    from main import ZotEyeApp


class About:

    def __init__(self, master, app: ZotEyeApp):
        self.master = master
        self.app = app
        self.font_14_bold = self.app.base_font.copy()
        self.font_14_bold.configure(size=14, weight="bold")
        self.font_10 = self.app.base_font.copy()
        self.font_10.configure(size=10)

    def show(self):
        about = tk.Toplevel(self.master)
        about.withdraw()

        about.title(APP_NAME)
        about.resizable(False, False)

        center_window(about, self.master, 350, 280)

        tk.Label(about, text=APP_NAME, font=self.font_14_bold).pack(pady=(10, 5))
        tk.Label(
            about,
            text=f"{self.app.translator.gettext('version')}: {APP_VERSION}",
            font=self.font_10,
        ).pack()
        tk.Label(
            about,
            text=self.app.translator.gettext("about_description"),
            font=self.font_10,
            wraplength=300,
            justify="center",
        ).pack(pady=(0, 15))
        tk.Label(
            about,
            text=f"{self.app.translator.gettext('author')}: {AUTHOR}",
            font=self.font_10,
        ).pack()
        tk.Label(
            about,
            text=f"{self.app.translator.gettext('publication_year')}: {PUBLICATION_YEAR}",
            font=self.font_10,
        ).pack()
        tk.Label(
            about, text=self.app.translator.gettext("license_mit"), font=self.font_10
        ).pack(pady=(0, 30))

        ttk.Button(
            about,
            style="Accent.TButton",
            text=self.app.translator.gettext("close"),
            command=about.destroy,
        ).pack(pady=(0, 10))

        # Make the dialog modal and bring it to focus
        about.transient(self.master)
        about.grab_set()
        about.focus_force()

        set_title_bar_dark(about, self.app.dark_theme_var.get())

        about.protocol("WM_DELETE_WINDOW", about.destroy)
        about.iconbitmap(ICO_PATH)
        about.deiconify()
