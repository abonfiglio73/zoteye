from __future__ import annotations
from tkinter import messagebox
from typing import TYPE_CHECKING
from logger import LogLevel
from config import APP_NAME, DB_SCHEMA_VERSION
from functions import compute_pdf_hash
from normalizer import normalize_sections
import os
import sqlite3

if TYPE_CHECKING:
    from main import ZotEyeApp


class NgramCache:

    def __init__(self, app: ZotEyeApp, db_file: str):
        self.db_file = db_file
        self.app = app
        self.ensure_schema()
        self.clean_ngram_cache()

    def ensure_schema(self):
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version TEXT
                )
            """
            )

            cur.execute("SELECT version FROM schema_version")
            row = cur.fetchone()

            if row is None:
                # New database
                cur.execute(
                    "INSERT INTO schema_version VALUES (?)",
                    (DB_SCHEMA_VERSION,),
                )
                self.create_tables(cur)
                return

            db_version = row[0]

            if db_version != DB_SCHEMA_VERSION:
                self.reset_database(cur, db_version)

    def reset_database(self, cur, old_version: int):
        # Retrieve indexed files
        try:
            cur.execute("SELECT db_path FROM ngram_dbs")
            db_paths = [r[0] for r in cur.fetchall()]
        except sqlite3.OperationalError:
            db_paths = []

        # Cancel files
        for path in db_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        # Drop tables
        cur.execute("DROP TABLE IF EXISTS ngram_dbs")
        cur.execute("DELETE FROM schema_version")

        # Recreate schema
        cur.execute(
            "INSERT INTO schema_version VALUES (?)",
            (DB_SCHEMA_VERSION,),
        )
        self.create_tables(cur)

        # Notification
        messagebox.showinfo(
            APP_NAME,
            self.app.translator.gettext("database_updated").format(
                old=old_version, new=DB_SCHEMA_VERSION
            ),
        )
        self.app.logger.log(
            f"{self.app.translator.gettext('database_updated').format(old=old_version, new=DB_SCHEMA_VERSION)}",
            LogLevel.INFO,
        )

    def create_tables(self, cur):
        cur.execute(
            """
            CREATE TABLE ngram_dbs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                db_path TEXT UNIQUE,
                pdf_hash TEXT,
                incremental_db BOOLEAN DEFAULT 1,
                ngram INTEGER DEFAULT 4,
                exclude_sections BOOLEAN DEFAULT 1,
                exclude_quotes BOOLEAN DEFAULT 1,
                sections_excluded TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    def clean_ngram_cache(self) -> int:
        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, db_path FROM ngram_dbs")
            rows = cur.fetchall()

            removed = 0
            for row_id, db_path in rows:
                if not db_path or not os.path.exists(db_path):
                    cur.execute(
                        "DELETE FROM ngram_dbs WHERE id = ?",
                        (row_id,),
                    )
                    removed += 1

            return removed

    def add_ngram_entry(
        self,
        db_path: str,
        incremental_db: bool,
        n: int,
        exclude_sections: bool,
        sections_excluded: str,
        exclude_quotes: bool,
        pdf_paths: list[str],
    ):

        sections_norm = normalize_sections(sections_excluded)
        pdf_hash = compute_pdf_hash(
            incremental_db,
            n,
            exclude_sections,
            sections_norm,
            exclude_quotes,
            pdf_paths,
        )

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR IGNORE INTO ngram_dbs (
                    db_path,
                    pdf_hash,
                    incremental_db,
                    ngram,
                    exclude_sections,
                    exclude_quotes,
                    sections_excluded
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    db_path,
                    pdf_hash,
                    incremental_db,
                    n,
                    exclude_sections,
                    exclude_quotes,
                    sections_norm,
                ),
            )

    def get_matching_ngram_db(
        self,
        incremental_db: bool,
        n: int,
        exclude_sections: bool,
        sections_excluded: str,
        exclude_quotes: bool,
        pdf_paths: list[str],
    ) -> str | None:

        sections_norm = normalize_sections(sections_excluded)
        pdf_hash = compute_pdf_hash(
            incremental_db,
            n,
            exclude_sections,
            sections_norm,
            exclude_quotes,
            pdf_paths,
        )

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT db_path
                FROM ngram_dbs
                WHERE pdf_hash = ?
                  AND incremental_db = ?
                  AND ngram = ?
                  AND exclude_sections = ?
                  AND sections_excluded = ?
                  AND exclude_quotes = ?
            """,
                (
                    pdf_hash,
                    incremental_db,
                    n,
                    exclude_sections,
                    sections_norm,
                    exclude_quotes,
                ),
            )

            row = cur.fetchone()

        return row[0] if row else None

    def get_ngram_dbs(
        self,
        incremental_db: bool,
        n: int,
        exclude_sections: bool,
        sections_excluded: str,
        exclude_quotes: bool,
    ) -> list[str]:

        sections_norm = normalize_sections(sections_excluded)

        with sqlite3.connect(self.db_file) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT db_path
                FROM ngram_dbs
                WHERE incremental_db = ?
                  AND ngram = ?
                  AND exclude_sections = ?
                  AND sections_excluded = ?
                  AND exclude_quotes = ?
                ORDER BY id DESC
            """,
                (
                    incremental_db,
                    n,
                    exclude_sections,
                    sections_norm,
                    exclude_quotes,
                ),
            )

            rows = cur.fetchall()

        return [r[0] for r in rows]
