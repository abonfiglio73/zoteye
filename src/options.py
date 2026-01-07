from __future__ import annotations
from typing import TYPE_CHECKING
from functions import set_title_bar_dark, center_window
from tooltip import ToolTip
from config import ICO_PATH
import tkinter as tk
import tkinter.ttk as ttk


if TYPE_CHECKING:
    from main import ZotEyeApp


class OptionsWindow:
    def __init__(self, master, app: ZotEyeApp):
        self.master = master
        self.app = app
        self.ToolTip = ToolTip

    def show(self):

        options = tk.Toplevel(self.master)

        options.withdraw()

        options.title(self.app.translator.gettext("options"))
        options.resizable(False, False)

        center_window(options, self.master, 750, 850)

        # --- N-gram section ---
        nrow = 1
        frame_gram = tk.LabelFrame(
            options,
            text=self.app.translator.gettext("parameters"),
            padx=10,
            pady=8,
            relief="groove",
            borderwidth=2,
        )
        frame_gram.grid(row=nrow, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        frame_row = ttk.Frame(frame_gram)
        frame_row.pack(fill="x", pady=3)
        ttk.Label(
            frame_row, text=f"{self.app.translator.gettext('number_ngrams')}:"
        ).pack(side="left")
        self.ngram_spin = ttk.Spinbox(
            frame_row,
            from_=2,
            to=10,
            width=3,
            textvariable=self.app.ngram_var,
            state="readonly",
        )
        self.ngram_spin.pack(side="left", padx=10)

        def toggle_sections_fields():
            state = "normal" if self.app.exclude_sections_var.get() else "disabled"
            self.sections_to_exclude_entry.config(state=state)

        frame_check = ttk.Frame(frame_gram)
        frame_check.pack(fill="x", pady=(5, 0), anchor="w")
        ttk.Checkbutton(
            frame_check,
            text=self.app.translator.gettext("exclude_sections"),
            variable=self.app.exclude_sections_var,
            command=toggle_sections_fields,
        ).pack(side="left", anchor="w")

        frame_row = ttk.Frame(frame_gram)
        frame_row.pack(fill="x", pady=3, padx=10)
        ttk.Label(frame_row, text=self.app.translator.gettext("sections")).pack(
            side="left"
        )
        self.sections_to_exclude_entry = ttk.Entry(
            frame_row, width=50, textvariable=self.app.sections_to_exclude_var
        )
        self.sections_to_exclude_entry.pack(side="left", padx=10)

        # Informative icon
        icon_sections = tk.Canvas(
            frame_row,
            width=20,
            height=20,
            highlightthickness=0,
            bg=frame_gram.cget("bg"),
        )
        icon_sections.pack(side="left", padx=10)
        icon_sections.create_oval(2, 2, 18, 18, fill="#0078D7", outline="")
        icon_sections.create_text(
            10, 10, text="?", fill="white", font=("Arial", 10, "bold")
        )

        self.ToolTip(
            icon_sections, self.app.translator.gettext("tooltip_exclude_sections")
        )

        ttk.Checkbutton(
            frame_gram,
            text=self.app.translator.gettext("exclude_citations"),
            variable=self.app.exclude_quotes_var,
        ).pack(anchor="w", pady=3)

        # --- Database section ---
        nrow += 1
        frame_db_ngram = tk.LabelFrame(
            options,
            text=self.app.translator.gettext("database_ngrams"),
            padx=10,
            pady=8,
            relief="groove",
            borderwidth=2,
        )
        frame_db_ngram.grid(
            row=nrow, column=0, columnspan=3, sticky="ew", padx=10, pady=5
        )

        def toggle_db_fields():
            state = "normal" if self.app.save_open_indexed_files.get() else "disabled"
            self.folder_db_n_gram_entry.config(state=state)
            self.folder_db_button.config(state=state)
            self.folder_db_open_button.config(state=state)
            self.rebuild_index_check.config(state=state)
            self.incremental_db_check.config(state=state)

        frame_row = ttk.Frame(frame_db_ngram)
        frame_row.pack(fill="x", pady=3)
        ttk.Checkbutton(
            frame_row,
            text=self.app.translator.gettext("open_save_database_ngrams"),
            variable=self.app.save_open_indexed_files,
            command=toggle_db_fields,
        ).pack(side="left")

        # Informative icon
        icon_db_ngram = tk.Canvas(
            frame_row,
            width=20,
            height=20,
            highlightthickness=0,
            bg=frame_db_ngram.cget("bg"),
        )
        icon_db_ngram.pack(side="left", padx=10)
        icon_db_ngram.create_oval(2, 2, 18, 18, fill="#0078D7", outline="")
        icon_db_ngram.create_text(
            10, 10, text="?", fill="white", font=("Arial", 10, "bold")
        )

        self.ToolTip(
            icon_db_ngram,
            self.app.translator.gettext("tooltip_open_save_database_ngrams"),
        )

        frame_row = ttk.Frame(frame_db_ngram)
        frame_row.pack(fill="x", pady=3, padx=10)

        ttk.Label(frame_row, text=f"{self.app.translator.gettext('path')}:").pack(
            side="left"
        )
        self.folder_db_n_gram_entry = ttk.Entry(
            frame_row, width=50, textvariable=self.app.folder_db_n_gram_var
        )
        self.folder_db_n_gram_entry.pack(side="left", padx=10)
        self.folder_db_button = ttk.Button(
            frame_row,
            style="Accent.TButton",
            text=self.app.translator.gettext("select"),
            command=lambda: self.app.FileDialogs.browse_folder(
                self.app.folder_db_n_gram_var,
                self.folder_db_n_gram_entry,
                title=self.app.translator.gettext("select_folder_database_ngrams"),
                db_folder=True,
            ),
        )
        self.folder_db_button.pack(side="left", padx=10)
        self.folder_db_open_button = ttk.Button(
            frame_row,
            style="Accent.TButton",
            text=self.app.translator.gettext("open"),
            command=lambda: self.app.FileDialogs.open_folder(
                self.app.folder_db_n_gram_var
            ),
        )
        self.folder_db_open_button.pack(side="left", padx=10)

        frame_row = ttk.Frame(frame_db_ngram)
        frame_row.pack(fill="x", pady=3, padx=10)
        self.incremental_db_check = ttk.Checkbutton(
            frame_row,
            text=self.app.translator.gettext("incremental_database"),
            variable=self.app.incremental_db_var,
            command=toggle_db_fields,
        )
        self.incremental_db_check.pack(anchor="w", side="left")

        # Informative icon
        icon_incremental_db = tk.Canvas(
            frame_row,
            width=20,
            height=20,
            highlightthickness=0,
            bg=frame_db_ngram.cget("bg"),
        )
        icon_incremental_db.pack(side="left", padx=10)
        icon_incremental_db.create_oval(2, 2, 18, 18, fill="#0078D7", outline="")
        icon_incremental_db.create_text(
            10, 10, text="?", fill="white", font=("Arial", 10, "bold")
        )

        self.ToolTip(
            icon_incremental_db,
            self.app.translator.gettext("tooltip_incremental_database"),
        )

        self.rebuild_index_check = ttk.Checkbutton(
            frame_db_ngram,
            text=self.app.translator.gettext("rebuild_database_ngrams"),
            variable=self.app.rebuild_index_var,
        )
        self.rebuild_index_check.pack(anchor="w", pady=3, padx=10)

        # --- Report section ---
        nrow += 1
        frame_report = tk.LabelFrame(
            options,
            text=self.app.translator.gettext("report"),
            padx=10,
            pady=8,
            relief="groove",
            borderwidth=2,
        )
        frame_report.grid(
            row=nrow, column=0, columnspan=3, sticky="ew", padx=10, pady=5
        )

        frame_row = ttk.Frame(frame_report)
        frame_row.pack(fill="x", pady=3)
        ttk.Label(frame_row, text=f"{self.app.translator.gettext('path')}:").pack(
            side="left"
        )
        self.folder_report_entry = ttk.Entry(
            frame_row, width=50, textvariable=self.app.folder_report_var
        )
        self.folder_report_entry.pack(side="left", padx=10)
        ttk.Button(
            frame_row,
            style="Accent.TButton",
            text=self.app.translator.gettext("select"),
            command=lambda: self.app.FileDialogs.browse_folder(
                self.app.folder_report_var,
                self.folder_report_entry,
                title=self.app.translator.gettext("select_folder_report"),
            ),
        ).pack(side="left", padx=10)
        ttk.Button(
            frame_row,
            style="Accent.TButton",
            text=self.app.translator.gettext("open"),
            command=lambda: self.app.FileDialogs.open_folder(
                self.app.folder_report_var
            ),
        ).pack(side="left", padx=10)

        ttk.Checkbutton(
            frame_report,
            text=self.app.translator.gettext("show_statistics"),
            variable=self.app.show_statistics_report_var,
        ).pack(anchor="w", pady=3)

        def toggle_more_similar_sentences_fields():
            state = (
                "readonly"
                if self.app.show_more_similar_sentences_var.get()
                else "disabled"
            )
            self.more_similar_ngram_entry.config(state=state)

        frame_row = ttk.Frame(frame_report)
        frame_row.pack(fill="x", pady=3, anchor="w")
        ttk.Checkbutton(
            frame_row,
            text=self.app.translator.gettext("show_more_similar_sentences"),
            variable=self.app.show_more_similar_sentences_var,
            command=toggle_more_similar_sentences_fields,
        ).pack(side="left", anchor="w")

        frame_row = ttk.Frame(frame_report)
        frame_row.pack(fill="x", pady=3, padx=10)
        ttk.Label(
            frame_row, text=f"{self.app.translator.gettext('number_ngrams')}:"
        ).pack(side="left")
        self.more_similar_ngram_entry = ttk.Spinbox(
            frame_row,
            from_=2,
            to=20,
            width=3,
            textvariable=self.app.more_similar_ngram_var,
            state="readonly",
        )
        self.more_similar_ngram_entry.pack(side="left", padx=10)

        def toggle_references_fields():
            state = (
                "normal" if self.app.show_references_report_var.get() else "disabled"
            )
            self.show_number_pages_entry.config(state=state)

        frame_row = ttk.Frame(frame_report)
        frame_row.pack(fill="x", pady=3, anchor="w")
        ttk.Checkbutton(
            frame_row,
            text=self.app.translator.gettext("show_references"),
            variable=self.app.show_references_report_var,
            command=toggle_references_fields,
        ).pack(side="left", anchor="w")

        frame_row = ttk.Frame(frame_report)
        frame_row.pack(fill="x", pady=3, padx=10)
        self.show_number_pages_entry = ttk.Checkbutton(
            frame_row,
            text=self.app.translator.gettext("show_number_pages"),
            variable=self.app.show_pagenum_report_var,
        )
        self.show_number_pages_entry.pack(side="left", padx=10)

        ttk.Checkbutton(
            frame_report,
            text=self.app.translator.gettext("open_report"),
            variable=self.app.open_pdf_var,
        ).pack(anchor="w", pady=3)

        # --- Update Section ---
        nrow += 1
        frame_update = tk.LabelFrame(
            options,
            text=self.app.translator.gettext("update"),
            padx=10,
            pady=8,
            relief="groove",
            borderwidth=2,
        )
        frame_update.grid(
            row=nrow, column=0, columnspan=3, sticky="ew", padx=10, pady=5
        )

        ttk.Checkbutton(
            frame_update,
            text=self.app.translator.gettext("check_update_at_startup"),
            variable=self.app.check_update_at_startup_var,
        ).pack(anchor="w", pady=3)

        # --- Close button ---
        nrow += 1
        closeButton = ttk.Button(
            options,
            style="Accent.TButton",
            text=self.app.translator.gettext("close"),
            # font=("Arial", 14),
            command=lambda: self.on_close_options(options),
        )
        closeButton.grid(row=nrow, column=1, pady=10)

        toggle_sections_fields()
        toggle_db_fields()
        toggle_more_similar_sentences_fields()
        toggle_references_fields()

        # --- Modal window ---
        options.transient(self.master)
        options.grab_set()
        options.focus_force()
        set_title_bar_dark(options, self.app.dark_theme_var.get())
        options.protocol("WM_DELETE_WINDOW", lambda: self.on_close_options(options))
        options.iconbitmap(ICO_PATH)
        options.deiconify()

    def on_close_options(self, win: tk.Toplevel):
        self.app.save_settings()
        win.destroy()
