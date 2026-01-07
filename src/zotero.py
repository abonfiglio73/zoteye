from normalizer import normalize_path
from pathlib import Path
from config import BASE_DIR_ZOTERO
import os
import sqlite3
import pandas as pd
import re
import configparser


def get_zotero_pdfs(zotero_db: str, collection_names: list[str]) -> list[str]:

    if isinstance(collection_names, str):
        collection_names = [collection_names]

    conn = sqlite3.connect(zotero_db)
    cursor = conn.cursor()

    # Build a map of collectionID: (name, parentCollectionID)
    cursor.execute(
        "SELECT collectionID, collectionName, parentCollectionID FROM collections"
    )
    collections = cursor.fetchall()
    coll_map = {cid: (name, parent) for cid, name, parent in collections}

    # Build the full hierarchical path of a collection
    def build_path(cid):
        name, parent = coll_map[cid]
        return (
            f"{build_path(parent)} / {name}" if parent and parent in coll_map else name
        )

    full_paths = {cid: build_path(cid) for cid in coll_map}

    # Find collection IDs that match the requested names
    wanted_ids = [cid for cid, path in full_paths.items() if path in collection_names]
    if not wanted_ids:
        conn.close()
        return []

    placeholders = ",".join("?" * len(wanted_ids))
    query = f"""
        SELECT c.collectionID, a.path, ia.key AS attachment_key
        FROM collections c
        JOIN collectionItems ci ON ci.collectionID = c.collectionID
        JOIN itemAttachments a ON a.parentItemID = ci.itemID
        JOIN items ia ON a.itemID = ia.itemID
        WHERE a.path LIKE 'storage:%' AND a.path LIKE '%.pdf'
          AND c.collectionID IN ({placeholders})
    """
    cursor.execute(query, wanted_ids)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    zotero_folder = os.path.dirname(zotero_db)
    storage_folder = os.path.join(zotero_folder, "storage")

    pdf_paths = []
    for _, rel_path, key in rows:
        # Zotero stores relative paths like 'storage:12345/filename.pdf'
        filename = rel_path.replace("storage:", "", 1)
        full_path = normalize_path(os.path.join(storage_folder, key, filename))
        if os.path.exists(full_path):
            pdf_paths.append(full_path)

    return pdf_paths


def get_zotero_collections(zotero_db: str) -> list[str]:

    conn = sqlite3.connect(zotero_db)

    query = """
        SELECT collectionID, collectionName, parentCollectionID
        FROM collections
        ORDER BY collectionName COLLATE NOCASE;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Build a mapping of collectionID: (name, parentID)
    coll_map = {
        row["collectionID"]: (row["collectionName"], row["parentCollectionID"])
        for _, row in df.iterrows()
    }

    def build_path(coll_id) -> str:
        name, parent_id = coll_map[coll_id]
        if parent_id and parent_id in coll_map:
            parent_path = build_path(parent_id)
            return f"{parent_path} / {name}"
        else:
            return name

    all_collections = [build_path(cid) for cid in coll_map]

    # Remove duplicates, sort case‑insensitively
    return sorted(set(all_collections), key=str.lower)


def find_database_zotero() -> Path:

    profiles_ini = BASE_DIR_ZOTERO / "profiles.ini"
    sqlite = Path()
    if profiles_ini.exists():
        cp = configparser.ConfigParser()
        cp.read(profiles_ini)

        for sec in cp.sections():
            if sec.startswith("Profile"):
                path_str = cp[sec]["Path"]
                is_relative = cp[sec].get("IsRelative", "1") == "1"
                profile = (
                    (BASE_DIR_ZOTERO / path_str) if is_relative else Path(path_str)
                )
                prefs = profile / "prefs.js"

                if prefs.exists():
                    text = prefs.read_text(errors="ignore")
                    m = re.search(
                        r'user_pref\("extensions\.zotero\.dataDir",\s*"(.*?)"\);', text
                    )
                    if m:
                        data_dir = Path(m.group(1))
                        sqlite = data_dir / "zotero.sqlite"
                    else:
                        default_dir = profile / "zotero"
                        sqlite = default_dir / "zotero.sqlite"
                    break
    return sqlite
