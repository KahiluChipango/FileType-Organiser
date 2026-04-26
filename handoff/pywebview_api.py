"""
FileType Organizer Pro — PyWebView API
======================================
This file exposes Python functions to the HTML frontend.
Every public method becomes callable from JavaScript as:
    await window.pywebview.api.method_name(args)
"""

import os
import sys
import json
import shutil
import threading
from datetime import datetime
from pathlib import Path


def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DEFAULT_EXT_MAP = """
PDF=Documents/PDF Files
DOCX=Documents/Word Files
DOC=Documents/Word Files
TXT=Documents/Text Files
XLSX=Documents/Excel Files
XLS=Documents/Excel Files
PPTX=Documents/PowerPoint Files
PPT=Documents/PowerPoint Files
MD=Documents/Markdown Files
CSV=Documents/CSV Files
RTF=Documents/Text Files
LOG=Documents/Log Files
EPUB=Documents/eBooks
JPG=Images/JPG Images
JPEG=Images/JPG Images
PNG=Images/PNG Images
GIF=Images/GIF Images
WEBP=Images/WebP Images
HEIC=Images/HEIC Images
SVG=Images/SVG Images
BMP=Images/BMP Images
TIFF=Images/TIFF Images
ICO=Images/Icons
RAW=Images/RAW Images
CR2=Images/RAW Images
NEF=Images/RAW Images
MP4=Videos/MP4 Videos
MKV=Videos/MKV Videos
MOV=Videos/MOV Videos
AVI=Videos/AVI Videos
WEBM=Videos/WebM Videos
FLV=Videos/FLV Videos
WMV=Videos/WMV Videos
MP3=Audio/MP3 Audio
WAV=Audio/WAV Audio
FLAC=Audio/FLAC Audio
AAC=Audio/AAC Audio
OGG=Audio/OGG Audio
M4A=Audio/M4A Audio
OPUS=Audio/Opus Audio
ZIP=Archives/ZIP Archives
RAR=Archives/RAR Archives
7Z=Archives/7Z Archives
TAR=Archives/TAR Archives
GZ=Archives/GZ Archives
BZ2=Archives/BZ2 Archives
ISO=Archives/ISO Archives
PY=Code/Python
JS=Code/JavaScript
TS=Code/TypeScript
HTML=Code/HTML
CSS=Code/CSS
JSON=Code/JSON
YAML=Code/YAML
YML=Code/YAML
SQL=Code/SQL
SH=Code/Shell
BAT=Code/Batch
JAVA=Code/Java
CPP=Code/C++
CS=Code/C#
GO=Code/Go
RS=Code/Rust
SWIFT=Code/Swift
EXE=Applications/Windows
MSI=Applications/Windows Installers
DMG=Applications/Mac
APK=Applications/Android
TTF=Fonts/TrueType
OTF=Fonts/OpenType
WOFF=Fonts/Web
WOFF2=Fonts/Web
"""


def _ensure_ext_map(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_EXT_MAP)


def _load_ext_map(path):
    _ensure_ext_map(path)
    m = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            ext, folder = line.split("=", 1)
            m[ext.strip().upper()] = folder.strip()
    return m


def _unique_name(dest_dir, fname):
    if not os.path.exists(os.path.join(dest_dir, fname)):
        return fname
    name, ext = os.path.splitext(fname)
    i = 1
    while os.path.exists(os.path.join(dest_dir, f"{name}_{i}{ext}")):
        i += 1
    return f"{name}_{i}{ext}"


class Api:
    """
    All public methods are exposed to JavaScript automatically by pywebview.
    Return values must be JSON-serialisable (dict, list, str, int, bool, None).
    """

    def __init__(self):
        self._window = None          # set by main.py after window creation
        self._settings = self._load_settings()
        self._progress_cb = None     # JS callback name for progress updates

    # ── Internal helpers ──────────────────────────────────────────────
    def _load_settings(self):
        defaults = {
            "master_folder_name": "Organised Files - FTO",
            "handle_duplicates": "rename",
            "recursive": False,
            "auto_organize": False,
            "exclude_patterns": [".DS_Store", "Thumbs.db", "desktop.ini", ".git"],
        }
        path = os.path.join(get_app_dir(), "settings.json")
        if os.path.exists(path):
            try:
                with open(path) as f:
                    defaults.update(json.load(f))
            except Exception:
                pass
        return defaults

    def _push(self, event: str, data: dict):
        """Send an event to the JS frontend via pywebview's evaluate_js."""
        if self._window:
            payload = json.dumps({"event": event, "data": data})
            self._window.evaluate_js(f"window.__bridge && window.__bridge({payload})")

    # ── Exposed API ───────────────────────────────────────────────────

    def pick_folder(self):
        """Open the OS folder picker and return the chosen path (or None)."""
        import webview
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            folder = result[0]
            return {"path": folder, "name": os.path.basename(folder)}
        return None

    def scan_folder(self, folder_path: str):
        """
        Quick scan — returns file counts per category and total size.
        Used to populate the stat cards after folder selection.
        """
        if not folder_path or not os.path.isdir(folder_path):
            return {"error": "Invalid folder"}

        ext_map = _load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
        counts = {}
        total_files = 0
        total_size = 0

        category_icons = {
            "Documents": "📄", "Images": "🖼", "Videos": "🎬",
            "Audio": "🎵", "Archives": "📦", "Code": "💻",
            "Applications": "⚙️", "Fonts": "🔤", "Other": "❓",
        }

        try:
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                if not os.path.isfile(fpath):
                    continue
                if any(p in fname for p in self._settings["exclude_patterns"]):
                    continue
                ext = Path(fname).suffix.lstrip(".").upper()
                if not ext:
                    continue
                dest = ext_map.get(ext, f"Other/{ext}")
                category = dest.split("/")[0]
                if category not in counts:
                    counts[category] = {"count": 0, "size": 0,
                                        "icon": category_icons.get(category, "📁")}
                counts[category]["count"] += 1
                counts[category]["size"] += os.path.getsize(fpath)
                total_files += 1
                total_size += os.path.getsize(fpath)
        except PermissionError:
            return {"error": "Permission denied"}

        return {
            "categories": counts,
            "total_files": total_files,
            "total_size": total_size,
            "total_size_mb": round(total_size / 1_048_576, 2),
        }

    def preview_folder(self, folder_path: str):
        """
        Returns the full planned move tree without moving anything.
        Used by the Preview screen.
        """
        if not folder_path or not os.path.isdir(folder_path):
            return {"error": "Invalid folder"}

        ext_map = _load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
        groups = {}
        total_files = 0
        total_size = 0
        skipped = 0

        try:
            for fname in os.listdir(folder_path):
                fpath = os.path.join(folder_path, fname)
                if not os.path.isfile(fpath):
                    continue
                if any(p in fname for p in self._settings["exclude_patterns"]):
                    skipped += 1
                    continue
                ext = Path(fname).suffix.lstrip(".").upper()
                if not ext:
                    skipped += 1
                    continue
                dest = ext_map.get(ext, f"Other/{ext}")
                size = os.path.getsize(fpath)
                if dest not in groups:
                    groups[dest] = {"files": [], "size": 0}
                groups[dest]["files"].append(fname)
                groups[dest]["size"] += size
                total_files += 1
                total_size += size
        except PermissionError:
            return {"error": "Permission denied"}

        return {
            "groups": groups,
            "total_files": total_files,
            "total_size_mb": round(total_size / 1_048_576, 2),
            "skipped": skipped,
        }

    def organize(self, folder_path: str):
        """
        Run the full organization. Runs in a background thread and pushes
        progress events to the frontend via window.__bridge().
        """
        if not folder_path or not os.path.isdir(folder_path):
            return {"error": "Invalid folder"}

        def _run():
            try:
                ext_map = _load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
                moved = renamed = skipped = 0
                total_size = 0
                log = {
                    "timestamp": datetime.now().isoformat(),
                    "source_folder": folder_path,
                    "files": [],
                }

                entries = []
                if self._settings["recursive"]:
                    for root, _, files in os.walk(folder_path):
                        if self._settings["master_folder_name"] in root:
                            continue
                        for f in files:
                            entries.append(os.path.join(root, f))
                else:
                    for f in os.listdir(folder_path):
                        p = os.path.join(folder_path, f)
                        if os.path.isfile(p):
                            entries.append(p)

                total = len(entries)
                self._push("progress_start", {"total": total})

                for i, fpath in enumerate(entries):
                    fname = os.path.basename(fpath)

                    if any(p in fname for p in self._settings["exclude_patterns"]):
                        skipped += 1
                        self._push("progress", {"current": i + 1, "total": total, "file": fname})
                        continue

                    ext = Path(fname).suffix.lstrip(".").upper()
                    if not ext:
                        skipped += 1
                        continue

                    master = os.path.join(folder_path, self._settings["master_folder_name"])
                    dest_dir = os.path.join(master, ext_map.get(ext, f"Other/{ext}"))
                    os.makedirs(dest_dir, exist_ok=True)

                    dest_name = fname
                    dup = self._settings["handle_duplicates"]
                    if os.path.exists(os.path.join(dest_dir, fname)):
                        if dup == "rename":
                            dest_name = _unique_name(dest_dir, fname)
                            renamed += 1
                        elif dup == "skip":
                            skipped += 1
                            continue

                    dest_path = os.path.join(dest_dir, dest_name)
                    try:
                        size = os.path.getsize(fpath)
                        shutil.move(fpath, dest_path)
                        log["files"].append({
                            "original_path": fpath,
                            "new_path": dest_path,
                            "size": size,
                        })
                        moved += 1
                        total_size += size
                    except Exception:
                        skipped += 1

                    self._push("progress", {
                        "current": i + 1, "total": total,
                        "file": fname, "pct": round((i + 1) / max(total, 1) * 100),
                    })

                # Save log
                if moved > 0:
                    log_path = os.path.join(get_app_dir(), "operation_log.json")
                    logs = []
                    if os.path.exists(log_path):
                        try:
                            with open(log_path) as f:
                                logs = json.load(f)
                        except Exception:
                            pass
                    logs.append(log)
                    with open(log_path, "w") as f:
                        json.dump(logs, f, indent=2)

                self._push("done", {
                    "moved": moved, "renamed": renamed,
                    "skipped": skipped,
                    "size_mb": round(total_size / 1_048_576, 2),
                    "master_folder": self._settings["master_folder_name"],
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "can_undo": moved > 0,
                })

            except Exception as e:
                self._push("error", {"message": str(e)})

        threading.Thread(target=_run, daemon=True).start()
        return {"status": "started"}

    def undo(self):
        """Restore files from the last operation log entry."""
        log_path = os.path.join(get_app_dir(), "operation_log.json")
        if not os.path.exists(log_path):
            return {"error": "No operations to undo"}
        try:
            with open(log_path) as f:
                logs = json.load(f)
        except Exception:
            return {"error": "Could not read operation log"}

        if not logs:
            return {"error": "No operations to undo"}

        last = logs[-1]
        restored = failed = 0
        for item in last["files"]:
            try:
                if os.path.exists(item["new_path"]):
                    os.makedirs(os.path.dirname(item["original_path"]), exist_ok=True)
                    shutil.move(item["new_path"], item["original_path"])
                    restored += 1
            except Exception:
                failed += 1

        logs.pop()
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)

        return {
            "restored": restored, "failed": failed,
            "has_more": len(logs) > 0,
        }

    def get_operation_logs(self):
        """Return the operation history for the Statistics screen."""
        log_path = os.path.join(get_app_dir(), "operation_log.json")
        if not os.path.exists(log_path):
            return []
        try:
            with open(log_path) as f:
                logs = json.load(f)
            result = []
            for log in reversed(logs[-20:]):
                total_size = sum(item.get("size", 0) for item in log.get("files", []))
                result.append({
                    "timestamp": log["timestamp"],
                    "source_folder": log["source_folder"],
                    "files_count": len(log.get("files", [])),
                    "size_mb": round(total_size / 1_048_576, 2),
                })
            return result
        except Exception:
            return []

    def get_settings(self):
        """Return current settings to populate the Settings screen."""
        return self._settings.copy()

    def save_settings(self, new_settings: dict):
        """Persist updated settings."""
        allowed = {"master_folder_name", "handle_duplicates",
                   "recursive", "auto_organize", "exclude_patterns"}
        for k, v in new_settings.items():
            if k in allowed:
                self._settings[k] = v
        path = os.path.join(get_app_dir(), "settings.json")
        with open(path, "w") as f:
            json.dump(self._settings, f, indent=2)
        return {"status": "ok"}

    def get_ext_map_text(self):
        """Return raw extension_map.txt content for the editor."""
        path = os.path.join(get_app_dir(), "extension_map.txt")
        _ensure_ext_map(path)
        with open(path, encoding="utf-8") as f:
            return f.read()

    def save_ext_map(self, content: str):
        """Save edited extension map."""
        path = os.path.join(get_app_dir(), "extension_map.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "ok"}

    def open_folder_in_explorer(self, folder_path: str):
        """Open a folder in the OS file manager."""
        import subprocess, platform
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
            return {"status": "ok"}
        except Exception as e:
            return {"error": str(e)}
