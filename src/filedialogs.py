from __future__ import annotations
from typing import TYPE_CHECKING
from tkinter import filedialog, messagebox
from config import APP_NAME
from normalizer import normalize_path
import os
import tkinter as tk

if TYPE_CHECKING:
    from main import ZotEyeApp


class FileDialogs:

    def __init__(self, app: ZotEyeApp):
        self.app = app

    def open_folder(self, var: tk.StringVar):
        path = var.get()
        if os.path.exists(path) and os.path.isdir(path):
            os.startfile(path)
        else:
            messagebox.showerror(
                APP_NAME, self.app.translator.gettext("error_folder_not_existing")
            )

    def open_file(self, var: tk.StringVar):
        path = var.get()
        if os.path.exists(path) and os.path.isfile(path):
            os.startfile(path)
        else:
            messagebox.showerror(
                APP_NAME, self.app.translator.gettext("error_file_not_existing")
            )

    def browse_folder(
        self, var: tk.StringVar, entry: tk.Entry, title: str, db_folder: bool = False
    ):

        current_value = var.get()
        if os.path.exists(current_value):
            initial_dir = os.path.dirname(current_value)
        else:
            initial_dir = os.getcwd()

        path = filedialog.askdirectory(initialdir=initial_dir, title=title)
        if path:
            if db_folder:
                if normalize_path(path) != self.app.folder_db_n_gram_var.get():
                    files = os.listdir(self.app.folder_db_n_gram_var.get())
                    has_db = any(f.endswith(".db") for f in files)
                    has_pkl = any(f.endswith(".pkl.gz") for f in files)
                    if has_db and has_pkl:
                        messagebox.showwarning(
                            APP_NAME,
                            self.app.translator.gettext(
                                "warning_change_ngram_db_folder"
                            ),
                        )
            entry.delete(0, tk.END)
            entry.insert(0, normalize_path(path))

    def browse_file(self, var: tk.StringVar, entry: tk.Entry, title: str, filetypes):

        path = var.get()
        initial_dir = os.path.dirname(path) if path else os.getcwd()
        initial_file = os.path.basename(path) if path else ""
        path = filedialog.askopenfilename(
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=filetypes,
            title=title,
        )
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, normalize_path(path))

    def browse_db(self):

        initial_dir = (
            os.path.dirname(self.app.db_zotero_var.get())
            if self.app.db_zotero_var.get()
            else os.getcwd()
        )
        initial_file = (
            os.path.basename(self.app.db_zotero_var.get())
            if self.app.db_zotero_var.get()
            else ""
        )
        path = filedialog.askopenfilename(
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=[("SQLite DB", "*.sqlite")],
            title=self.app.translator.gettext("select_database"),
        )
        if path:
            self.app.zotero_db_entry.delete(0, tk.END)
            self.app.zotero_db_entry.insert(0, normalize_path(path))
