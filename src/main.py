from cmenubutton import CustomMenuButton
from updater import Updater
from ngramcache import NgramCache
from translator import Translator
from tkinter import messagebox, ttk
from extractor import extract_text
from report import print_report
from normalizer import normalize_path, normalize_sections
from ngrams import build_ngram_index, calculate_similarity
from input_output import InputOutput
from tkinter import messagebox, ttk
from zotero import get_zotero_pdfs, get_zotero_collections, find_database_zotero
from config import (
    THEME_PATH,
    DOWNLOADS_DIR,
    LOG_FILE,
    APP_NAME,
    APP_VERSION,
    OWNER,
    REPO,
    SETTINGS_FILE,
    ICO_PATH,
    LOCALAPPDATA,
    DB_FILE,
    LOCALES_PATH,
    ENV_PATH,
    DOC_PATH,
)
from functions import (
    get_docx_text_hash,
    compute_pdf_hash,
    get_pdfs_from_folder,
    write_log,
    convert_docx_to_pdf,
    set_title_bar_dark,
    center_window,
    detect_dark_theme,
    detect_language,
)
from filedialogs import FileDialogs
from options import OptionsWindow
from about import About
from dotenv import load_dotenv
from logger import Logger, LogLevel
import shutil
import os
import json
import sys
import tempfile
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import traceback
import traceback
import threading
import datetime
import ctypes
import webbrowser


class ZotEyeApp:

    def change_theme(self):
        theme_key = "dark" if self.dark_theme_var.get() else "light"
        theme = self.themes[theme_key]
        for btn in self.menu_buttons:
            btn.bg = theme["bg"]
            btn.fg = theme["fg"]
            btn.active_bg = theme["active_bg"]
            btn.active_fg = theme["active_fg"]
            btn.hover_bg = theme["hover_bg"]
            btn.border_color = theme["border_color"]
            btn.refresh_style()
        self.set_theme(theme_key)
        set_title_bar_dark(self.root, self.dark_theme_var.get())

    def set_theme(self, theme: str):
        style = ttk.Style()
        style.theme_use(f"sun-valley-{theme}")
        style.configure("TButton", font=self.base_font)
        style.configure("TRadiobutton", font=self.base_font)
        style.configure("TCheckbutton", font=self.base_font)

    def unhandled_exception(self, exc_type, exc_value, exc_tb):
        err_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        write_log(err_text)
        messagebox.showerror(
            APP_NAME,
            f"{self.translator.gettext('error_unhandled_exception')}:\n{LOG_FILE}.",
        )

    def find_db_zotero(self):
        sqlite = find_database_zotero()
        if sqlite and sqlite.exists():
            messagebox.showinfo(
                APP_NAME,
                f"{self.translator.gettext('path_db_zotero_found')}: {str(sqlite)}",
            )
            self.db_zotero_var.set(str(sqlite))
        else:
            messagebox.showwarning(
                APP_NAME, self.translator.gettext("path_db_zotero_not_found")
            )

    def update_listbox_collections(self, event=None):
        if self.updating_listbox:
            return

        self.updating_listbox = True
        zotero_db = self.db_zotero_var.get().strip()
        self.zotero_collection_listbox.delete(0, tk.END)

        if zotero_db and os.path.exists(zotero_db):

            collections = get_zotero_collections(zotero_db)

            for col in collections:
                self.zotero_collection_listbox.insert(tk.END, col)

            selected_names = []
            val = self.collection_var.get()
            if val:
                selected_names = [c.strip() for c in val.split(";")]

            for i, col in enumerate(collections):
                if col in selected_names:
                    self.zotero_collection_listbox.selection_set(i)
        else:
            self.zotero_collection_listbox.insert(
                tk.END,
                f"— {self.translator.gettext('error_no_collection_available')} —",
            )

        self.updating_listbox = False

    def update_mode(self):

        zotero_widgets = [
            self.zotero_db_label,
            self.zotero_db_entry,
            self.zotero_db_button,
            self.zotero_db_find_button,
            self.zotero_collection_label,
            self.zotero_collection_listbox,
        ]

        single_widgets = [
            self.file_label,
            self.file_entry,
            self.file_button,
            self.file_open_button,
        ]

        folder_widgets = [
            self.folder_label,
            self.folder_entry,
            self.folder_button,
            self.folder_open_button,
        ]

        def set_state(widgets, state):
            for w in widgets:
                w.configure(state=state)

        mode = self.mode_var.get()

        set_state(zotero_widgets, "normal" if mode == "zotero" else "disabled")
        set_state(single_widgets, "normal" if mode == "single" else "disabled")
        set_state(folder_widgets, "normal" if mode == "folder" else "disabled")

    def about(self):
        about = About(self.root, app=self)
        about.show()

    def options(self):
        options = OptionsWindow(self.root, app=self)
        options.show()

    def check_update_threaded(self, print_status: bool = True):
        thread = threading.Thread(
            target=self.check_update, args=(print_status,), daemon=True
        )
        thread.start()

    def check_update(self, print_status: bool = True):

        Updater(
            owner=OWNER,
            repo=REPO,
            local_version=APP_VERSION,
            root=self.root,
            app=self,
            download_dir=DOWNLOADS_DIR,
            token=os.getenv("GITHUB_TOKEN"),
            restart_callback=lambda: self.root.destroy(),
            print_status=print_status,
        ).check_and_update()

    def filter_pdf_ngram_index(self, pdf_paths) -> dict:
        pdf_paths = set(pdf_paths)
        result = {}
        for pdf_path, data in self.pdf_ngram_index.items():
            if pdf_path in pdf_paths:
                result[pdf_path] = data
        return result

    def __init__(self, root):

        # Load enviromental variables such as GITHUB_TOKEN (necessary for private repositories) from file .env
        load_dotenv(dotenv_path=ENV_PATH, override=True)

        self.root = root

        # This is used to capture unhandled exceptions that could block the application if not managed
        self.root.report_callback_exception = self.unhandled_exception

        self.base_font = tkFont.nametofont("TkDefaultFont")
        self.base_font.configure(family="Segoe UI", size=12)
        self.root.option_add("*Font", self.base_font)
        self.root.title(APP_NAME)

        # Set the icon in the taskbar (Windows)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"{APP_NAME}.app")
        # Set the icon for the window
        root.iconbitmap(ICO_PATH)
        self.translator = Translator(locales_dir=LOCALES_PATH)
        self.io = InputOutput(self)
        self.FileDialogs = FileDialogs(self)
        self.logger = Logger(self)
        center_window(root, None, 793, 890)
        root.resizable(False, False)

        self.pdf_ngram_index = {}
        self.stop_flag = False
        self.temp_dir = os.path.join(tempfile.gettempdir(), f"{APP_NAME}")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.file_cache = {}
        self.db_hash = ""
        self.updating_listbox = False

        self.language_var = tk.StringVar(value=detect_language())

        self.mode_var = tk.StringVar(value="zotero")
        self.target_var = tk.StringVar()
        self.file_var = tk.StringVar()
        self.folder_var = tk.StringVar()

        self.folder_db_n_gram_var = tk.StringVar(
            value=normalize_path(os.path.join(LOCALAPPDATA, "db"))
        )
        self.db_zotero_var = tk.StringVar()

        self.collection_var = tk.StringVar()
        self.folder_report_var = tk.StringVar(
            value=normalize_path(os.path.join(LOCALAPPDATA, "reports"))
        )

        self.ngram_var = tk.IntVar(value=4)
        self.exclude_sections_var = tk.BooleanVar(value=True)
        self.sections_to_exclude_var = tk.StringVar(
            value="references;bibliography;acknowledgments;appendix;appendices"
        )
        self.exclude_quotes_var = tk.BooleanVar(value=True)

        self.save_open_indexed_files = tk.BooleanVar(value=True)
        self.incremental_db_var = tk.BooleanVar(value=True)
        self.rebuild_index_var = tk.BooleanVar(value=False)

        self.show_more_similar_sentences_var = tk.BooleanVar(value=True)
        self.more_similar_ngram_var = tk.IntVar(value=8)
        self.show_references_report_var = tk.BooleanVar(value=True)
        self.show_pagenum_report_var = tk.BooleanVar(value=True)
        self.show_statistics_report_var = tk.BooleanVar(value=True)
        self.open_pdf_var = tk.BooleanVar(value=True)
        self.check_update_at_startup_var = tk.BooleanVar(value=True)
        self.dark_theme_var = tk.BooleanVar(value=detect_dark_theme())

        # Theme colors
        self.themes = {
            "dark": {
                "bg": "#292929",
                "fg": "#fafafa",
                "active_bg": "#595959",
                "active_fg": "#ffffff",
                "hover_bg": "#57c8ff",
                "border_color": "#1c1c1c",
            },
            "light": {
                "bg": "#e7e7e7",
                "fg": "#1c1c1c",
                "active_bg": "#a0a0a0",
                "active_fg": "#ffffff",
                "hover_bg": "#005fb8",
                "border_color": "#fafafa",
            },
        }

        # Load settings
        self.load_settings()

        # Set the language used for strings
        if not self.translator.load_language(self.language_var.get()):
            messagebox.showerror(
                APP_NAME,
                "Impossible to load the language file. The file is missing or corrupted. Try to uninstall and install the app again.",
            )
            sys.exit()

        if not os.path.exists(self.folder_db_n_gram_var.get()):
            os.makedirs(self.folder_db_n_gram_var.get(), exist_ok=True)

        nrow = 0
        # --- Top Bar ---
        menu_bar = ttk.Frame(root)
        menu_bar.grid(row=nrow, column=0, sticky="ew", padx=5, pady=5)

        # --- Options Menu with CustomMenuButton ---
        self.menu_file_button = CustomMenuButton(
            menu_bar,
            text="File",
            font=self.base_font,
            options=[(self.translator.gettext("options"), "", self.options)],
        )
        self.menu_file_button.grid(row=nrow, column=0, padx=5, pady=5)

        # --- Language Menu with CustomMenuButton ---
        options = []
        for lang_code in self.translator.get_available_languages():
            options.append(
                (
                    lang_code.upper(),
                    lang_code,
                    lambda lc=lang_code: self.change_language(lc),
                )
            )

        self.menu_lang_button = CustomMenuButton(
            menu_bar,
            text=self.translator.gettext("language"),
            options=options,
            variable=self.language_var,
            font=self.base_font,
        )

        self.menu_lang_button.grid(row=nrow, column=1, padx=5, pady=5)

        # --- Help Menu with CustomMenuButton ---
        self.menu_help_button = CustomMenuButton(
            menu_bar,
            text=self.translator.gettext("help"),
            font=self.base_font,
            options=[
                (
                    self.translator.gettext("documentation"),
                    "",
                    lambda: webbrowser.open(DOC_PATH),
                ),
                (
                    self.translator.gettext("check_update"),
                    "",
                    lambda: self.check_update_threaded(print_status=True),
                ),
                ("separator", None, None),
                ("About", "", self.about),
            ],
        )
        self.menu_help_button.grid(row=nrow, column=2, padx=5, pady=5)

        # List of all menu buttons created used for changing the theme
        self.menu_buttons = [
            self.menu_file_button,
            self.menu_lang_button,
            self.menu_help_button,
        ]

        # Checkbutton for dark or light theme
        dark_theme = ttk.Checkbutton(
            menu_bar,
            style="Switch.TCheckbutton",
            text=self.translator.gettext("dark_theme"),
            variable=self.dark_theme_var,
            command=self.change_theme,
        )
        dark_theme.grid(row=nrow, column=3, padx=5, pady=5)

        # --- Frame for target document to compare ---
        nrow += 1
        target_frame = tk.LabelFrame(
            root, text=self.translator.gettext("target_document"), padx=10, pady=10
        )
        target_frame.grid(
            row=nrow, column=0, columnspan=4, sticky="ew", padx=10, pady=5
        )
        ttk.Label(target_frame, text="File:").pack(side="left")
        self.target_entry = ttk.Entry(
            target_frame, width=50, textvariable=self.target_var
        )
        self.target_entry.pack(side="left", padx=10)
        ttk.Button(
            target_frame,
            style="Accent.TButton",
            text=self.translator.gettext("select"),
            command=lambda: self.FileDialogs.browse_file(
                self.target_var,
                self.target_entry,
                title=self.translator.gettext("select_document"),
                filetypes=[(self.translator.gettext("documents"), "*.pdf *.docx")],
            ),
        ).pack(side="left", padx=5)
        ttk.Button(
            target_frame,
            style="Accent.TButton",
            text=self.translator.gettext("open"),
            command=lambda: self.FileDialogs.open_file(self.target_var),
        ).pack(side="left", padx=5)

        # --- Frame for comparison mode ---
        nrow += 1
        mode_frame = tk.LabelFrame(
            root, text=self.translator.gettext("mode_comparison"), padx=10, pady=10
        )
        mode_frame.grid(row=nrow, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        frame_row = 0

        # 1) Single PDF
        ttk.Radiobutton(
            mode_frame,
            text=self.translator.gettext("mode_single"),
            variable=self.mode_var,
            value="single",
            command=self.update_mode,
        ).grid(row=frame_row, column=0, sticky="w")
        frame_row += 1
        self.file_label = ttk.Label(
            mode_frame, text=f"{self.translator.gettext('path')}:"
        )
        self.file_entry = ttk.Entry(mode_frame, width=50, textvariable=self.file_var)
        self.file_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("select"),
            command=lambda: self.FileDialogs.browse_file(
                self.file_var,
                self.file_entry,
                title=self.translator.gettext("select_document"),
                filetypes=[(self.translator.gettext("documents"), "*.pdf")],
            ),
        )
        self.file_open_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("open"),
            command=lambda: self.FileDialogs.open_file(self.file_var),
        )
        self.file_label.grid(padx=10, row=frame_row, column=0, sticky="w")
        self.file_entry.grid(row=frame_row, column=1)
        self.file_button.grid(padx=10, row=frame_row, column=2)
        self.file_open_button.grid(padx=10, row=frame_row, column=3)
        frame_row += 1

        # 2) PDF Folder
        ttk.Radiobutton(
            mode_frame,
            text=self.translator.gettext("mode_folder"),
            variable=self.mode_var,
            value="folder",
            command=self.update_mode,
        ).grid(row=frame_row, column=0, sticky="w")
        frame_row += 1
        self.folder_label = ttk.Label(
            mode_frame, text=f"{self.translator.gettext('path')}:"
        )
        self.folder_entry = ttk.Entry(
            mode_frame, width=50, textvariable=self.folder_var
        )
        self.folder_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("select"),
            command=lambda: self.FileDialogs.browse_folder(
                self.folder_var,
                self.folder_entry,
                title=self.translator.gettext("select_folder"),
            ),
        )
        self.folder_open_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("open"),
            command=lambda: self.FileDialogs.open_folder(self.folder_var),
        )
        self.folder_label.grid(padx=10, row=frame_row, column=0, sticky="w")
        self.folder_entry.grid(row=frame_row, column=1)
        self.folder_button.grid(padx=10, row=frame_row, column=2)
        self.folder_open_button.grid(padx=10, row=frame_row, column=3)
        frame_row += 1

        # 3) Zotero
        ttk.Radiobutton(
            mode_frame,
            text="Zotero",
            variable=self.mode_var,
            value="zotero",
            command=self.update_mode,
        ).grid(row=frame_row, column=0, sticky="w")
        frame_row += 1
        self.zotero_db_label = ttk.Label(mode_frame, text="Database:")
        self.zotero_db_entry = ttk.Entry(
            mode_frame, width=50, textvariable=self.db_zotero_var
        )
        self.zotero_db_find_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("find"),
            command=self.find_db_zotero,
        )
        self.zotero_db_button = ttk.Button(
            mode_frame,
            style="Accent.TButton",
            text=self.translator.gettext("select"),
            command=self.FileDialogs.browse_db,
        )
        self.zotero_db_label.grid(padx=10, row=frame_row, column=0, sticky="w")
        self.zotero_db_entry.grid(row=frame_row, column=1)
        self.zotero_db_find_button.grid(padx=10, row=frame_row, column=2)
        self.zotero_db_button.grid(padx=10, row=frame_row, column=3)

        frame_row += 1
        self.zotero_collection_label = ttk.Label(
            mode_frame, text=f"{self.translator.gettext('collections')}:"
        )
        self.zotero_collection_label.grid(padx=10, row=frame_row, column=0, sticky="w")

        listbox_frame = ttk.Frame(mode_frame)
        listbox_frame.grid(row=frame_row, column=1, sticky="nsew")

        self.scrollbar_listbox_v = ttk.Scrollbar(listbox_frame, orient="vertical")
        self.scrollbar_listbox_v.pack(side="right", fill="y")
        self.scrollbar_listbox_h = ttk.Scrollbar(listbox_frame, orient="horizontal")
        self.scrollbar_listbox_h.pack(side="bottom", fill="x")

        self.zotero_collection_listbox = tk.Listbox(
            listbox_frame,
            selectmode="extended",
            yscrollcommand=self.scrollbar_listbox_v.set,
            xscrollcommand=self.scrollbar_listbox_h.set,
            height=5,  # number of elements shown
            width=40,
            activestyle="none",
            selectbackground="#d9d9d9",
            selectforeground="black",
        )
        self.scrollbar_listbox_v.config(command=self.zotero_collection_listbox.yview)
        self.scrollbar_listbox_h.config(command=self.zotero_collection_listbox.xview)
        self.zotero_collection_listbox.pack(side="left", fill="both", expand=True)

        def on_listbox_selection_change(event):

            if self.updating_listbox:
                return
            listbox = event.widget
            selected_indices = listbox.curselection()
            selected_names = [listbox.get(i) for i in selected_indices]
            self.collection_var.set(";".join(selected_names))

        self.zotero_collection_listbox.bind(
            "<<ListboxSelect>>", on_listbox_selection_change
        )
        self.db_zotero_var.trace_add(
            "write", lambda *args: self.update_listbox_collections()
        )

        # --- Log Frame ---
        nrow += 1
        log_frame = tk.LabelFrame(
            root, text=self.translator.gettext("log_analysis"), padx=10, pady=10
        )
        log_frame.grid(row=nrow, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)

        scrollbar_v = ttk.Scrollbar(log_frame, orient="vertical")
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h = ttk.Scrollbar(log_frame, orient="horizontal")
        scrollbar_h.pack(side="bottom", fill="x")
        self.log_text = tk.Text(
            log_frame,
            width=50,
            height=10,
            state="disabled",
            wrap="none",
            yscrollcommand=scrollbar_v.set,
            xscrollcommand=scrollbar_h.set,
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar_v.config(command=self.log_text.yview)
        scrollbar_h.config(command=self.log_text.xview)

        # --- Progress bar ---
        self.progress_frame = ttk.Frame(root)
        nrow += 1
        self.progress_frame.grid(row=nrow, column=0, columnspan=4, pady=5, sticky="ew")
        inner_frame = ttk.Frame(self.progress_frame)
        inner_frame.pack(expand=True)
        self.progress = ttk.Progressbar(
            inner_frame, orient="horizontal", length=550, mode="determinate"
        )
        self.progress.pack(side="left")
        self.progress_label = ttk.Label(inner_frame, text="")
        self.progress_label.pack(side="left", padx=4)
        self.progress["value"] = 0

        # Buttons for running and stopping the similarity analysis
        nrow += 1
        buttons_frame = ttk.Frame(root)
        buttons_frame.grid(row=nrow, column=0, columnspan=4, pady=10)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self.start_button = ttk.Button(
            buttons_frame,
            style="Accent.TButton",
            text=self.translator.gettext("run_analysis"),
            command=self.run_analysis_threaded,
        )
        self.start_button.grid(row=0, column=0, padx=50)
        self.start_button.config(state="normal")

        self.stop_button = ttk.Button(
            buttons_frame,
            style="Accent.TButton",
            text=f"🟥 {self.translator.gettext('stop_analysis')}",
            command=self.stop_analysis,
        )
        self.stop_button.grid(row=0, column=1, padx=50)
        self.stop_button.config(state="disabled")

        # Update Zotero collections
        try:
            self.update_listbox_collections()
        except Exception as e:
            messagebox.showerror(
                APP_NAME, self.translator.gettext("error_reading_zotero_collections")
            )
            self.zotero_collection_listbox.insert(
                tk.END,
                f"— {self.translator.gettext('error_collection_zotero_not_found')} —",
            )
            self.logger.log(
                f"{self.translator.gettext('error_collection_zotero_not_found')}",
                LogLevel.ERROR,
            )

        # Show/hide widgets based on comparison mode
        self.update_mode()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.tk.call("source", THEME_PATH)
        self.change_theme()

    def on_close(self):
        self.save_settings()
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                pass
        self.root.destroy()
        self.root.quit()

    def change_language(self, lang_code):
        self.language_var.set(lang_code)
        messagebox.showinfo(APP_NAME, self.translator.gettext("info_change_language"))

    def stop_analysis(self):
        self.stop_flag = True
        self.logger.log(
            f"{self.translator.gettext('stop_action_requested')}", LogLevel.STOP
        )

    def save_settings(self):
        settings = {
            "language": self.language_var.get(),
            "target_pdf": self.target_var.get(),
            "mode_var": self.mode_var.get(),
            "file_pdf": self.file_var.get(),
            "folder_pdf": self.folder_var.get(),
            "db_zotero": self.db_zotero_var.get(),
            "folder_db_n_gram": self.folder_db_n_gram_var.get(),
            "collection": self.collection_var.get(),
            "n_gram": self.ngram_var.get(),
            "exclude_sections": self.exclude_sections_var.get(),
            "sections_to_exclude": self.sections_to_exclude_var.get(),
            "exclude_quotes": self.exclude_quotes_var.get(),
            "open_pdf": self.open_pdf_var.get(),
            "folder_report": self.folder_report_var.get(),
            "show_more_similar_sentences": self.show_more_similar_sentences_var.get(),
            "more_similar_ngram": self.more_similar_ngram_var.get(),
            "show_references_report": self.show_references_report_var.get(),
            "show_pagenum_report": self.show_pagenum_report_var.get(),
            "show_statistics_report": self.show_statistics_report_var.get(),
            "save_open_indexed_files": self.save_open_indexed_files.get(),
            "incremental_db": self.incremental_db_var.get(),
            "check_update_at_startup": self.check_update_at_startup_var.get(),
            "dark_theme": self.dark_theme_var.get(),
        }
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def load_settings(self):

        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.language_var.set(settings.get("language", "en"))
                self.target_var.set(settings.get("target_pdf", ""))
                self.mode_var.set(settings.get("mode_var", "zotero"))  # default
                self.file_var.set(settings.get("file_pdf", ""))
                self.folder_var.set(settings.get("folder_pdf", ""))
                self.db_zotero_var.set(settings.get("db_zotero", ""))
                self.folder_db_n_gram_var.set(
                    settings.get(
                        "folder_db_n_gram",
                        normalize_path(os.path.join(LOCALAPPDATA, "db")),
                    )
                )
                self.collection_var.set(settings.get("collection", ""))
                self.ngram_var.set(settings.get("n_gram", 4))
                self.exclude_sections_var.set(settings.get("exclude_sections", True))
                self.sections_to_exclude_var.set(
                    settings.get(
                        "sections_to_exclude",
                        "references;bibliography;acknowledgments;appendix;appendices",
                    )
                )
                self.exclude_quotes_var.set(settings.get("exclude_quotes", True))
                self.open_pdf_var.set(settings.get("open_pdf", True))

                self.show_more_similar_sentences_var.set(
                    settings.get("show_more_similar_sentences", True)
                )
                self.more_similar_ngram_var.set(settings.get("more_similar_ngram", 8))

                self.show_references_report_var.set(
                    settings.get("show_references_report", True)
                )
                self.show_pagenum_report_var.set(
                    settings.get("show_pagenum_report", True)
                )
                self.show_statistics_report_var.set(
                    settings.get("show_statistics_report", True)
                )
                self.folder_report_var.set(
                    settings.get(
                        "folder_report",
                        normalize_path(os.path.join(LOCALAPPDATA, "reports")),
                    )
                )
                self.save_open_indexed_files.set(
                    settings.get("save_open_indexed_files", True)
                )
                self.incremental_db_var.set(settings.get("incremental_db", True)),
                self.check_update_at_startup_var.set(
                    settings.get("check_update_at_startup", True)
                )
                self.dark_theme_var.set(settings.get("dark_theme", True))

    def run_analysis_threaded(self):
        thread = threading.Thread(target=self.run_analysis, daemon=True)
        thread.start()

    def run_analysis(self):

        self.stop_flag = False
        self.results = []
        self.progress["value"] = 0
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.start_button.config(state="disabled")

        target_pdf = self.target_entry.get()
        if not os.path.exists(target_pdf):
            messagebox.showerror(
                APP_NAME, self.translator.gettext("error_target_document_not_found")
            )
            self.logger.log(
                f"{self.translator.gettext('error_target_document_not_found')}",
                LogLevel.ERROR,
            )
            self.start_button.config(state="normal")
            return

        ext_target = os.path.splitext(target_pdf)[1].lower()
        if ext_target != ".docx" and ext_target != ".pdf":
            messagebox.showerror(
                APP_NAME, self.translator.gettext("error_format_document")
            )
            self.logger.log(
                f"{self.translator.gettext('error_format_document')}",
                LogLevel.ERROR,
            )
            self.start_button.config(state="normal")
            return

        pdf_paths = []
        if self.mode_var.get() == "single":
            file_path = self.file_entry.get()
            if not os.path.exists(file_path):
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_document_not_found")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_document_not_found')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return
            pdf_paths = [file_path]
        elif self.mode_var.get() == "folder":
            folder_path = self.folder_entry.get()
            if not os.path.exists(folder_path):
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_folder_not_found")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_folder_not_found')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return
            pdf_paths = get_pdfs_from_folder(folder_path, recursive=True)
            if not pdf_paths:
                messagebox.showinfo(
                    APP_NAME, self.translator.gettext("error_documents_not_found")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_documents_not_found')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return
        elif self.mode_var.get() == "zotero":

            db = self.zotero_db_entry.get()
            if not os.path.exists(db):
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_database_zotero_not_found")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_database_zotero_not_found')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return

            selected_indices = self.zotero_collection_listbox.curselection()
            if not selected_indices:
                messagebox.showerror(
                    APP_NAME,
                    self.translator.gettext("error_collection_zotero_not_found"),
                )
                self.logger.log(
                    f"{self.translator.gettext('error_collection_zotero_not_found')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return
            selected_names = [
                self.zotero_collection_listbox.get(i) for i in selected_indices
            ]

            try:
                pdf_paths = get_zotero_pdfs(db, selected_names)
            except Exception as e:
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_reading_documents_zotero")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_reading_documents_zotero')}",
                    LogLevel.ERROR,
                )
                self.zotero_collection_listbox.selection_clear(0, tk.END)
                self.start_button.config(state="normal")
                return
            if not pdf_paths:
                messagebox.showerror(
                    APP_NAME,
                    self.translator.gettext(
                        "error_no_documents_found_in_zotero_collection"
                    ),
                )
                self.logger.log(
                    f"{self.translator.gettext('error_no_documents_found_in_zotero_collection')}",
                    LogLevel.ERROR,
                )
                self.start_button.config(state="normal")
                return

        if self.save_open_indexed_files.get():

            db_file = os.path.join(self.folder_db_n_gram_var.get(), DB_FILE)
            self.ngram_cache = NgramCache(self, db_file=db_file)

            try:
                if not self.incremental_db_var.get():
                    pickle_path = self.ngram_cache.get_matching_ngram_db(
                        self.incremental_db_var.get(),
                        self.ngram_var.get(),
                        self.exclude_sections_var.get(),
                        self.sections_to_exclude_var.get(),
                        self.exclude_quotes_var.get(),
                        pdf_paths,
                    )
                else:
                    pickle_paths = self.ngram_cache.get_ngram_dbs(
                        self.incremental_db_var.get(),
                        self.ngram_var.get(),
                        self.exclude_sections_var.get(),
                        self.sections_to_exclude_var.get(),
                        self.exclude_quotes_var.get(),
                    )
                    existing_paths = [p for p in pickle_paths if os.path.exists(p)]
            except Exception as e:
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_reading_database")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_reading_database')}",
                    LogLevel.ERROR,
                )
                answer = messagebox.askyesno(
                    APP_NAME, self.translator.gettext("question_run_analysis")
                )
                if answer:
                    self.pdf_ngram_index = {}
                    existing_paths = []
                    pickle_path = ""
                    self.logger.log(
                        f"{self.translator.gettext('database_rebuilt')}",
                        LogLevel.INFO,
                    )
                else:
                    self.start_button.config(state="normal")
                    return

            db_hash = compute_pdf_hash(
                self.incremental_db_var.get(),
                self.ngram_var.get(),
                self.exclude_sections_var.get(),
                normalize_sections(self.sections_to_exclude_var.get()),
                self.exclude_quotes_var.get(),
                pdf_paths,
            )
            if (
                not self.incremental_db_var.get()
                and pickle_path
                and os.path.exists(pickle_path)
            ) or (self.incremental_db_var.get() and existing_paths):

                if self.rebuild_index_var.get():
                    answer = messagebox.askyesno(
                        APP_NAME,
                        self.translator.gettext("question_rebuilding_database"),
                    )
                    if answer:
                        if not self.incremental_db_var.get():
                            os.remove(pickle_path)
                        else:
                            for p in existing_paths:
                                os.remove(p)
                        self.pdf_ngram_index = {}
                        self.logger.log(
                            f"{self.translator.gettext('database_rebuilt')}",
                            LogLevel.INFO,
                        )
                    else:
                        self.rebuild_index_var.set(False)
                else:
                    if not self.pdf_ngram_index or db_hash != self.db_hash:
                        if not self.incremental_db_var.get():
                            self.logger.log(
                                f"{self.translator.gettext('database_found')}: {pickle_path}",
                                LogLevel.INFO,
                            )
                        else:
                            self.logger.log(
                                f"{self.translator.gettext('incremental_database_found')}",
                                LogLevel.INFO,
                            )
                        try:
                            if not self.incremental_db_var.get():
                                self.pdf_ngram_index = self.io.load_ngram_index(
                                    pickle_path=pickle_path
                                )
                            else:
                                merged = {}
                                for p in existing_paths:
                                    part = self.io.load_ngram_index(pickle_path=p)
                                    merged.update(part)
                                self.pdf_ngram_index = merged
                            self.db_hash = db_hash
                        except Exception as e:
                            messagebox.showerror(
                                APP_NAME,
                                self.translator.gettext(
                                    "error_loading_incremental_database"
                                ),
                            )
                            self.logger.log(
                                f"{self.translator.gettext('error_loading_incremental_database')}",
                                LogLevel.ERROR,
                            )
                            self.pdf_ngram_index = {}
            else:
                self.logger.log(
                    f"{self.translator.gettext('no_database_found_index_rebuilded')}",
                    LogLevel.INFO,
                )
                self.pdf_ngram_index = {}
        else:
            self.pdf_ngram_index = {}

        self.logger.log(f"{self.translator.gettext('started_analysis')}", LogLevel.RUN)
        if ext_target == ".docx":
            docx_path = target_pdf
            current_hash = get_docx_text_hash(docx_path)
            cache_entry = self.file_cache.get(docx_path)
            if (
                cache_entry
                and cache_entry["hash"] == current_hash
                and os.path.exists(cache_entry["pdf"])
            ):
                target_pdf = cache_entry["pdf"]
            else:
                if cache_entry and os.path.exists(cache_entry["pdf"]):
                    os.remove(cache_entry["pdf"])
                fd, tmp_pdf_path = tempfile.mkstemp(suffix=".pdf", dir=self.temp_dir)
                os.close(fd)
                self.logger.log(
                    f"{self.translator.gettext('converting_document')}",
                    LogLevel.WORKING,
                )
                if not convert_docx_to_pdf(docx_path, tmp_pdf_path):
                    messagebox.showerror(
                        APP_NAME, self.translator.gettext("error_converting_document")
                    )
                    self.logger.log(
                        f"{self.translator.gettext('error_converting_document')}",
                        LogLevel.ERROR,
                    )
                    self.start_button.config(state="normal")
                    return
                self.file_cache[docx_path] = {
                    "hash": current_hash,
                    "pdf": tmp_pdf_path,
                }
                target_pdf = tmp_pdf_path

        target_df = extract_text(
            target_pdf,
            self.exclude_sections_var.get(),
            self.sections_to_exclude_var.get(),
            self.exclude_quotes_var.get(),
        )

        pdf_ngram_index_selected = self.filter_pdf_ngram_index(pdf_paths)
        to_index = [p for p in pdf_paths if p not in self.pdf_ngram_index]
        total_to_index = len(to_index)

        total_to_compare = (
            len(pdf_ngram_index_selected)
            if pdf_ngram_index_selected
            else len(pdf_paths)
        )

        self.logger.log(
            self.translator.gettext("documents_found").format(
                to_compare=total_to_compare, to_index=total_to_index
            ),
            LogLevel.STATISTICS,
        )
        self.progress["maximum"] = total_to_index + 2

        self.stop_button.config(state="normal")
        self.save_db = False
        pdf_ngram_index_new = {}
        for i, pdf_path in enumerate(to_index, start=1):
            if self.stop_flag:
                self.logger.log(
                    f"{self.translator.gettext('stopped_analysis')}",
                    LogLevel.WARNING,
                )
                break
            pdf_name = os.path.basename(pdf_path)
            other_df = extract_text(
                pdf_path,
                self.exclude_sections_var.get(),
                self.sections_to_exclude_var.get(),
                self.exclude_quotes_var.get(),
            )
            if other_df is None:
                self.logger.log(
                    f"{self.translator.gettext('unable_extracting_text')}",
                    LogLevel.WARNING,
                    pdf_path=pdf_path,
                )
            else:
                pdf_index_df = build_ngram_index(other_df, n=self.ngram_var.get())
                self.pdf_ngram_index[pdf_path] = pdf_index_df
                if self.save_open_indexed_files.get():
                    self.save_db = True
                    pdf_ngram_index_new[pdf_path] = pdf_index_df

                self.logger.log(
                    f"{self.translator.gettext('loaded_indexed_document')} {i}/{total_to_index} → {pdf_name}",
                    LogLevel.INFO,
                )

            self.progress["value"] = i
            percent = int(i / self.progress["maximum"] * 100)
            self.progress_label.config(text=f"{percent}%")
            self.root.update_idletasks()

        self.stop_button.config(state="disabled")

        if self.save_db:
            try:

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                pickle_path = normalize_path(
                    os.path.join(
                        self.folder_db_n_gram_var.get(), f"db_ngram_{timestamp}.pkl.gz"
                    )
                )

                if not self.incremental_db_var.get():
                    self.io.save_ngram_index(
                        self.pdf_ngram_index, pickle_path=pickle_path
                    )
                else:
                    if pdf_ngram_index_new:
                        self.io.save_ngram_index(
                            pdf_ngram_index_new, pickle_path=pickle_path
                        )

                self.ngram_cache.add_ngram_entry(
                    pickle_path,
                    self.incremental_db_var.get(),
                    self.ngram_var.get(),
                    self.exclude_sections_var.get(),
                    self.sections_to_exclude_var.get(),
                    self.exclude_quotes_var.get(),
                    pdf_paths,
                )
                self.db_hash = compute_pdf_hash(
                    self.incremental_db_var.get(),
                    self.ngram_var.get(),
                    self.exclude_sections_var.get(),
                    normalize_sections(self.sections_to_exclude_var.get()),
                    self.exclude_quotes_var.get(),
                    pdf_paths,
                )
            except Exception as e:
                messagebox.showerror(
                    APP_NAME, self.translator.gettext("error_saving_database")
                )
                self.logger.log(
                    f"{self.translator.gettext('error_saving_database')}",
                    LogLevel.ERROR,
                )
            self.stop_button.config(state="disabled")
        self.logger.log(
            f"{self.translator.gettext('calculating_similarity')}",
            LogLevel.ELABORATE,
        )

        pdf_ngram_index_selected = self.filter_pdf_ngram_index(pdf_paths)
        target_ngram_index = build_ngram_index(target_df, n=self.ngram_var.get())

        results, overall_similarity, max_similarity, avg_similarity = (
            calculate_similarity(target_ngram_index, pdf_ngram_index_selected)
        )
        self.logger.log(
            f"{self.translator.gettext('overall_percentage')}: {overall_similarity:.2f}%",
            LogLevel.STATISTICS,
        )
        self.logger.log(
            f"{self.translator.gettext('max_percentage')}: {max_similarity:.2f}%",
            LogLevel.STATISTICS,
        )
        self.logger.log(
            f"{self.translator.gettext('average_percentage')}: {avg_similarity:.2f}%",
            LogLevel.STATISTICS,
        )
        self.progress["value"] = total_to_index + 1
        percent = int((total_to_index + 1) / self.progress["maximum"] * 100)
        self.progress_label.config(text=f"{percent}%")
        self.root.update_idletasks()
        self.logger.log(
            f"{self.translator.gettext('creating_report')}", LogLevel.ELABORATE
        )
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name_report = f"report_{APP_NAME.lower()}_{timestamp}.pdf"
        if not os.path.exists(self.folder_report_var.get()):
            os.makedirs(self.folder_report_var.get(), exist_ok=True)
        path_report = normalize_path(
            os.path.join(self.folder_report_var.get(), name_report)
        )

        print_report(
            target_df,
            target_ngram_index,
            pdf_ngram_index_selected,
            output_pdf=path_report,
            n=self.ngram_var.get(),
            overall_similarity=overall_similarity,
            per_pdf_scores=results,
            show_more_similar_sentences=self.show_more_similar_sentences_var.get(),
            more_similar_ngram=self.more_similar_ngram_var.get(),
            show_references=self.show_references_report_var.get(),
            show_pagenum=self.show_pagenum_report_var.get(),
            show_statistics=self.show_statistics_report_var.get(),
            translator=self.translator,
        )

        self.logger.log(
            f"{self.translator.gettext('created_report')}",
            LogLevel.SUCCESS,
            pdf_path=path_report,
        )

        self.progress["value"] = total_to_index + 2
        percent = int((total_to_index + 2) / self.progress["maximum"] * 100)
        self.progress_label.config(text=f"{percent}%")
        self.root.update_idletasks()
        if self.open_pdf_var.get():
            try:
                os.startfile(path_report)
                self.logger.log(
                    f"{self.translator.gettext('opened_report')}", LogLevel.OPEN
                )
            except Exception as e:
                self.logger.log(
                    f"{self.translator.gettext('error_opening_report')}: {e}",
                    LogLevel.ERROR,
                )

        self.progress["value"] = 0
        self.progress_label.config(text="")
        self.start_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = ZotEyeApp(root)
    root.update_idletasks()
    root.deiconify()
    if app.check_update_at_startup_var.get():
        root.update()
        app.check_update_threaded(print_status=False)
    root.mainloop()
