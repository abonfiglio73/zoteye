# ----------------------------------------------------------------
# Module to estimate the size of the installation folder.
# This is necessary since venv (along with the required libraries)
# is created during installation by the NSIS installer
# ----------------------------------------------------------------
import os

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # src/
assets_dir = os.path.abspath(os.path.join(src_dir, "..", "assets"))  # root/assets
venv_dir = os.path.abspath(os.path.join(src_dir, "..", "venv"))  # root/venv

folders = [src_dir, assets_dir, venv_dir]

total_bytes = 0
for folder in folders:
    for dirpath, dirnames, filenames in os.walk(folder):
        if "utils" in dirnames:
            dirnames.remove("utils")

        for f in filenames:
            try:
                total_bytes += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass

total_kb = total_bytes / 1024  # KB
print(int(total_kb))
