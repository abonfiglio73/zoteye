from winreg import (
    HKEY_CURRENT_USER as hkey,
    QueryValueEx as getSubkeyValue,
    OpenKey as getKey,
)
from normalizer import normalize_path
from config import LOG_FILE, APP_NAME
from docx import Document
import msvcrt
import datetime
import winreg
import pythoncom
import win32com.client
import os
import ctypes
import tkinter as tk
import locale
import hashlib


def get_docx_text_hash(docx_path):
    doc = Document(docx_path)
    text = "\n".join(p.text for p in doc.paragraphs)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_pdf_hash(
    incremental_db: bool,
    ngram: int,
    exclude_sections: bool,
    sections_excluded: str,
    exclude_quotes: bool,
    pdf_paths: list[str],
) -> str:

    sha = hashlib.sha256()

    # Files
    for path in sorted(pdf_paths):
        sha.update(f"path={path}".encode("utf-8"))

        if os.path.exists(path):
            stat = os.stat(path)
            sha.update(f"size={stat.st_size}".encode("utf-8"))
            sha.update(f"mtime={int(stat.st_mtime)}".encode("utf-8"))
        else:
            sha.update(b"missing")

    # Parameters (order-independent)
    params = {
        "incremental_db": int(incremental_db),
        "ngram": int(ngram),
        "exclude_sections": int(exclude_sections),
        "exclude_quotes": int(exclude_quotes),
        "sections_excluded": sections_excluded or "",
    }

    for key in sorted(params):
        sha.update(f"{key}={params[key]}".encode("utf-8"))

    return sha.hexdigest()


def get_pdfs_from_folder(folder_path: str, recursive: bool = True) -> list[str]:

    pdf_paths = []

    if recursive:
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    pdf_paths.append(normalize_path(os.path.join(root, file)))
    else:
        pdf_paths = [
            normalize_path(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.lower().endswith(".pdf")
        ]

    return pdf_paths


def is_file_open(path: str) -> bool:
    try:
        with open(path, "r+b") as f:
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        return False
    except OSError:
        return True


def convert_docx_to_pdf(docx_path: str, output_path: str) -> bool:

    if is_file_open(docx_path):
        return False

    pythoncom.CoInitialize()
    word = None
    doc = None

    try:
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0

        doc = word.Documents.Open(
            docx_path, ReadOnly=True, AddToRecentFiles=False, ConfirmConversions=False
        )

        doc.SaveAs(output_path, FileFormat=17)
        return True

    except Exception:
        return False

    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()
        pythoncom.CoUninitialize()


def write_log(err_text):

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        f.write(err_text)
        f.write("\n")


def set_title_bar_dark(window, enable=True):

    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

    value = 2 if enable else 0  # 2 = dark, 0 = light
    c_value = ctypes.c_int(value)

    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd, 20, ctypes.byref(c_value), ctypes.sizeof(c_value)
    )


def get_windows_workarea():
    SPI_GETWORKAREA = 0x0030
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
    )
    return rect.left, rect.top, rect.right, rect.bottom


def center_window(win: tk.Toplevel, parent: tk.Widget | None, width: int, height: int):
    win.update_idletasks()

    if parent is None:
        left, top, right, bottom = get_windows_workarea()
        work_w = right - left
        work_h = bottom - top

        x = left + (work_w - width) // 2
        y = top + (work_h - height) // 2

    else:
        parent.update_idletasks()

        px = parent.winfo_rootx()
        py = parent.winfo_rooty()

        pw = parent.winfo_width()
        ph = parent.winfo_height()

        titlebar = parent.winfo_rooty() - parent.winfo_y()

        center_x = px + pw // 2
        center_y = py + ph // 2 - titlebar

        x = center_x - width // 2
        y = center_y - height // 2

    win.geometry(f"{width}x{height}+{x}+{y}")


def detect_dark_theme() -> bool:

    valueMeaning = {0: True, 1: False}
    try:
        key = getKey(
            hkey, "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
        )
        subkey = getSubkeyValue(key, "AppsUseLightTheme")[0]
    except FileNotFoundError:
        return False
    return valueMeaning[subkey]


def lcid_to_language(lcid: int) -> str | None:
    loc = locale.windows_locale.get(lcid)
    if not loc:
        return None
    return loc.split("_")[0]


def detect_language() -> str:
    # 1) Check the registry
    try:
        REG_PATH = rf"Software\{APP_NAME}"
        REG_VALUE = "InstallerLanguage"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            value, regtype = winreg.QueryValueEx(key, REG_VALUE)

            if isinstance(value, int):
                lang = lcid_to_language(value)
                if lang:
                    return lang

    except FileNotFoundError:
        pass
    except OSError:
        pass

    # 2) Fallback: use the system language of Windows
    lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    return lcid_to_language(lcid) or "en"
