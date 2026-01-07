# ---------------------------------------------
# Module to create the structure of the project
# ----------------------------------------------
import os
import sys

EXCLUDE_DIRS = {"venv", ".git", "__pycache__", "data"}

EXCLUDE_FILES = {
    "tree.md",
    "README.md",
}

EXCLUDE_EXT = {".log"}

ICONS = {
    "folder": "📁",
    "file": "📄",
    ".py": "🐍",
    ".json": "🧾",
    ".md": "📘",
    ".txt": "📝",
    ".csv": "📊",
    ".jpg": "🖼️",
    ".jpeg": "🖼️",
    ".png": "🖼️",
    ".html": "🌐",
    ".css": "🎨",
    ".js": "📜",
    ".exe": "⚙️",
    ".pdf": "📕",
}


def get_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ICONS.get(ext, ICONS["file"])


def is_excluded(path, name):
    ext = os.path.splitext(name)[1].lower()

    if os.path.isdir(path) and name in EXCLUDE_DIRS:
        return True

    if name in EXCLUDE_FILES:
        return True

    if ext in EXCLUDE_EXT:
        return True

    return False


def generate_tree_md(path, prefix=""):
    lines = []

    entries = [
        e for e in sorted(os.listdir(path)) if not is_excluded(os.path.join(path, e), e)
    ]

    total = len(entries)

    for i, name in enumerate(entries):
        full = os.path.join(path, name)
        connector = "└── " if i == total - 1 else "├── "
        new_prefix = "    " if i == total - 1 else "│   "

        if os.path.isdir(full):
            icon = ICONS["folder"]
            lines.append(f"{prefix}{connector}{icon} {name}/")
            lines.extend(generate_tree_md(full, prefix + new_prefix))
        else:
            icon = get_icon(name)
            lines.append(f"{prefix}{connector}{icon} {name}")

    return lines


def write_tree_md(folder):
    folder = os.path.abspath(folder)
    root_name = os.path.basename(folder)

    md_lines = []
    md_lines.append(f"# 📂 Directory Tree for `{root_name}`\n")
    md_lines.append("```text")
    md_lines.append(f"{ICONS['folder']} {root_name}/")
    md_lines.extend(generate_tree_md(folder))
    md_lines.append("```")

    project_root = os.path.abspath(os.path.dirname(__file__))
    output_file = os.path.join(project_root, "..", "..", "tree.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"✅ File Markdown generated: {output_file}")


if __name__ == "__main__":

    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    write_tree_md(folder)
