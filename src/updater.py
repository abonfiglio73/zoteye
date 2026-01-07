from __future__ import annotations
from typing import TYPE_CHECKING
from tkinter import ttk, messagebox
from packaging import version
from config import APP_NAME, ICO_PATH
from functions import center_window, set_title_bar_dark
import os
import threading
import hashlib
import requests
import tkinter as tk

if TYPE_CHECKING:
    from main import ZotEyeApp


class UpdaterBase:

    def __init__(
        self, owner: str, repo: str, local_version: str, token: str | None = None
    ):

        self.owner = owner
        self.repo = repo
        self.local_version = local_version
        self.token = token

    def _headers(self, extra: dict | None = None) -> dict:
        h: dict[str, str] = {}
        if self.token:
            h["Authorization"] = f"token {self.token}"
        if extra:
            h.update(extra)
        return h

    def get_latest_release(self) -> dict:
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        r = requests.get(url, headers=self._headers())
        r.raise_for_status()
        return r.json()

    def normalize_version(self, v: str) -> str:
        v = v.lower().lstrip("v").replace("_", "-")
        import re

        m = re.match(r"(alpha|beta|rc)[-]?(\d+\.\d+\.\d+)", v)
        if m:
            stage = {"alpha": "a", "beta": "b", "rc": "rc"}[m.group(1)]
            return f"{m.group(2)}{stage}0"
        return v

    def check_for_update(self) -> tuple[str, dict] | None:
        data = self.get_latest_release()
        latest = data["tag_name"]

        norm_local = version.parse(self.normalize_version(self.local_version))
        norm_latest = version.parse(self.normalize_version(latest))

        if norm_latest <= norm_local:
            return None

        assets = data.get("assets", [])
        if not assets:
            raise RuntimeError("No assets available in the release")

        asset = next((a for a in assets if a["name"].endswith(".exe")), assets[0])
        return latest, asset

    def download_asset(self, asset: dict, dest: str, progress_callback=None) -> str:
        if self.token:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/assets/{asset['id']}"
            headers = self._headers({"Accept": "application/octet-stream"})
        else:
            url = asset["browser_download_url"]
            headers = {}

        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            done = 0

            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if self.cancel_download:
                        return None
                    if not chunk:
                        continue
                    f.write(chunk)
                    done += len(chunk)
                    if progress_callback:
                        progress_callback(done, total)

        return dest

    def verify_sha256(self, file_path: str, expected_sha256: str) -> bool:
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
        return sha.hexdigest().lower() == expected_sha256.lower()

    def run_installer(self, path: str):
        os.startfile(path)


class Updater(UpdaterBase):

    def __init__(
        self,
        owner,
        repo,
        local_version,
        root,
        app: ZotEyeApp,
        download_dir=".",
        token=None,
        restart_callback=None,
        print_status=True,
    ):
        super().__init__(owner, repo, local_version, token)

        self.root = root
        self.app = app
        self.download_dir = download_dir
        self.restart_callback = restart_callback
        self.print_status = print_status
        self.cancel_download = False

    def check_and_update(self):
        try:
            res = self.check_for_update()
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"{self.app.translator.gettext('error_checking_update')}: \n{e}",
            )
            return

        if not res:
            if self.print_status:

                messagebox.showinfo(
                    APP_NAME, self.app.translator.gettext("no_update_available")
                )
            return

        latest, asset = res

        answer = messagebox.askyesno(
            APP_NAME,
            self.app.translator.gettext("update_available").format(latest=latest),
        )
        if not answer:
            return

        self._start_download(asset)

    def _start_download(self, asset):
        self.asset = asset
        self.dl_win = tk.Toplevel(self.root)
        self.dl_win.withdraw()
        self.dl_win.title(APP_NAME)
        self.dl_win.resizable(False, False)
        self.dl_win.iconbitmap(ICO_PATH)

        center_window(self.dl_win, self.root, 420, 160)

        tk.Label(
            self.dl_win, text=self.app.translator.gettext("downloading_update")
        ).pack(pady=10)

        self.progress = ttk.Progressbar(self.dl_win, length=380, mode="determinate")
        self.progress.pack(pady=5)

        self.dl_label = tk.Label(self.dl_win, text="")
        self.dl_label.pack()

        self.cancel_btn = ttk.Button(
            self.dl_win,
            text=self.app.translator.gettext("cancel"),
            command=self._cancel_download,
        )
        self.cancel_btn.pack(pady=10)
        self.dl_win.protocol("WM_DELETE_WINDOW", self._cancel_download)
        self.dl_win.transient(self.root)
        self.dl_win.grab_set()
        self.dl_win.focus_force()
        set_title_bar_dark(self.dl_win, self.app.dark_theme_var.get())
        self.dl_win.deiconify()

        threading.Thread(target=self._download_thread, daemon=True).start()

    def _progress_callback(self, done, total):
        self.root.after(0, lambda: self._update_progress(done, total))

    def _update_progress(self, done, total):
        try:
            if total > 0:
                pct = (done / total) * 100
                self.progress["value"] = pct
                self.dl_label.config(text=f"{done/1024:.1f} KB / {total/1024:.1f} KB")
            else:
                self.dl_label.config(text=f"{done/1024:.1f} KB / ?")
        except tk.TclError:
            pass

    def _download_thread(self):
        asset = self.asset
        name = asset["name"]
        dest = os.path.join(self.download_dir, name)

        try:
            result = self.download_asset(asset, dest, self._progress_callback)
            if result is None:
                self.root.after(
                    0,
                    lambda: messagebox.showinfo(
                        APP_NAME, self.app.translator.gettext("download_canceled")
                    ),
                )
                return
            if "sha256" in asset:
                if not self.verify_sha256(dest, asset["sha256"]):
                    raise RuntimeError(self.app.translator.gettext("checksum_mismatch"))
        except Exception as e:
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    APP_NAME,
                    f"{self.app.translator.gettext('error_downloading_update')}: \n{e}",
                ),
            )
            return

        self.root.after(0, self._finish_download, dest)

    def _cancel_download(self):
        self.cancel_download = True
        try:
            self.dl_win.destroy()
        except:
            pass

    def _finish_download(self, path):

        self.dl_win.destroy()

        if not messagebox.askyesno(
            APP_NAME, self.app.translator.gettext("download_completed")
        ):
            return

        if self.restart_callback:
            self.restart_callback()

        try:
            self.run_installer(path)
        except Exception as e:
            messagebox.showerror(
                APP_NAME,
                f"{self.app.translator.gettext('error_start_installer')}: \n{e}",
            )
            return
