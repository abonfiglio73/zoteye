from pathlib import Path
import os
import winreg

APP_NAME = "ZotEye"
APP_VERSION = "1.0.0"
AUTHOR = "Andrea Bonfiglio"
PUBLICATION_YEAR = "2026"
REPO = "zoteye"
OWNER = "abonfiglio73"

BASE_DIR = Path(__file__).resolve().parent
DOC_PATH = Path("https://github.com", OWNER, REPO, "blob", "master", "README.md")

LOCALAPPDATA = Path(os.getenv("LOCALAPPDATA")) / APP_NAME / "data"
if not LOCALAPPDATA.exists():
    LOCALAPPDATA = BASE_DIR / ".." / "data"

ICO_PATH = BASE_DIR / ".." / "assets" / "icons" / f"{APP_NAME}.ico"
if not ICO_PATH.exists():
    ICO_PATH = BASE_DIR / "assets" / "icons" / f"{APP_NAME}.ico"

LOCALES_PATH = BASE_DIR / ".." / "assets" / "locales"
if not LOCALES_PATH.exists():
    LOCALES_PATH = BASE_DIR / "assets" / "locales"

THEME_PATH = BASE_DIR / ".." / "assets" / "theme" / "sv.tcl"
if not THEME_PATH.exists():
    THEME_PATH = BASE_DIR / "assets" / "theme" / "sv.tcl"

ENV_PATH = Path(BASE_DIR, ".env")

DB_FILE = "db_ngram.db"
DB_SCHEMA_VERSION = "1.0"
LOG_FILE = LOCALAPPDATA / "zoteye.log"
SETTINGS_FILE = LOCALAPPDATA / "settings.json"

BASE_DIR_ZOTERO = Path(os.getenv("APPDATA")) / "Zotero" / "Zotero"

try:
    sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
        downloads, _ = winreg.QueryValueEx(
            key, "{374DE290-123F-4565-9164-39C4925E467B}"
        )
    DOWNLOADS_DIR = Path(downloads)
except Exception:
    DOWNLOADS_DIR = Path(os.getenv("USERPROFILE")) / "Downloads"

if not DOWNLOADS_DIR.exists():
    DOWNLOADS_DIR = BASE_DIR / "downloads"
