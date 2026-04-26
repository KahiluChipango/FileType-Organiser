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
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__) if not getattr(sys, "frozen", False) else os.path.dirname(sys.executable), 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
        try:
            import webview
            logger.info("Opening folder picker dialog")
            result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
            if result and len(result) > 0:
                folder = result[0]
                if not os.path.exists(folder):
                    logger.error(f"Selected folder does not exist: {folder}")
                    return {"error": "Selected folder does not exist"}
                if not os.path.isdir(folder):
                    logger.error(f"Selected path is not a folder: {folder}")
                    return {"error": "Please select a folder, not a file"}
                logger.info(f"Folder selected: {folder}")
                return {"path": folder, "name": os.path.basename(folder)}
            logger.info("Folder selection cancelled")
            return None
        except Exception as e:
            logger.error(f"Error in pick_folder: {str(e)}", exc_info=True)
            return {"error": f"Failed to open folder picker: {str(e)}"}

    def scan_folder(self, folder_path: str):
        """
        Quick scan — returns file counts per category and total size.
        Used to populate the stat cards after folder selection.
        """
        try:
            if not folder_path:
                logger.warning("scan_folder called with empty path")
                return {"error": "Folder path is required"}

            if not os.path.exists(folder_path):
                logger.error(f"Folder does not exist: {folder_path}")
                return {"error": "Folder does not exist"}

            if not os.path.isdir(folder_path):
                logger.error(f"Path is not a directory: {folder_path}")
                return {"error": "Path is not a directory"}

            logger.info(f"Scanning folder: {folder_path}")
            ext_map = _load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
            counts = {}
            total_files = 0
            total_size = 0
            skipped_files = 0

            category_icons = {
                "Documents": "📄", "Images": "🖼", "Videos": "🎬",
                "Audio": "🎵", "Archives": "📦", "Code": "💻",
                "Applications": "⚙️", "Fonts": "🔤", "Other": "❓",
            }

            try:
                files = os.listdir(folder_path)
                logger.info(f"Found {len(files)} items in folder")

                for fname in files:
                    fpath = os.path.join(folder_path, fname)

                    # Skip directories
                    if not os.path.isfile(fpath):
                        continue

                    # Skip excluded patterns
                    if any(p in fname for p in self._settings["exclude_patterns"]):
                        skipped_files += 1
                        continue

                    # Skip files without extensions
                    ext = Path(fname).suffix.lstrip(".").upper()
                    if not ext:
                        skipped_files += 1
                        continue

                    try:
                        file_size = os.path.getsize(fpath)
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Could not get size of {fname}: {e}")
                        skipped_files += 1
                        continue

                    dest = ext_map.get(ext, f"Other/{ext}")
                    category = dest.split("/")[0]

                    if category not in counts:
                        counts[category] = {
                            "count": 0,
                            "size": 0,
                            "icon": category_icons.get(category, "📁")
                        }

                    counts[category]["count"] += 1
                    counts[category]["size"] += file_size
                    total_files += 1
                    total_size += file_size

                logger.info(f"Scan complete: {total_files} files, {skipped_files} skipped")

            except PermissionError as e:
                logger.error(f"Permission denied accessing folder: {folder_path}", exc_info=True)
                return {"error": "Permission denied: Cannot access this folder"}
            except OSError as e:
                logger.error(f"OS error scanning folder: {str(e)}", exc_info=True)
                return {"error": f"Cannot read folder: {str(e)}"}

            return {
                "categories": counts,
                "total_files": total_files,
                "total_size": total_size,
                "total_size_mb": round(total_size / 1_048_576, 2),
                "skipped_files": skipped_files,
            }

        except Exception as e:
            logger.error(f"Unexpected error in scan_folder: {str(e)}", exc_info=True)
            return {"error": f"Scan failed: {str(e)}"}

    def preview_folder(self, folder_path: str):
        """
        Returns the full planned move tree without moving anything.
        Used by the Preview screen.
        """
        try:
            if not folder_path:
                return {"error": "Folder path is required"}

            if not os.path.exists(folder_path):
                return {"error": "Folder does not exist"}

            if not os.path.isdir(folder_path):
                return {"error": "Path is not a directory"}

            logger.info(f"Previewing folder organization: {folder_path}")
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

                    try:
                        size = os.path.getsize(fpath)
                    except (OSError, PermissionError):
                        skipped += 1
                        continue

                    if dest not in groups:
                        groups[dest] = {"files": [], "size": 0}

                    groups[dest]["files"].append(fname)
                    groups[dest]["size"] += size
                    total_files += 1
                    total_size += size

            except PermissionError:
                logger.error(f"Permission denied previewing folder: {folder_path}")
                return {"error": "Permission denied: Cannot access this folder"}
            except OSError as e:
                logger.error(f"OS error previewing folder: {str(e)}")
                return {"error": f"Cannot read folder: {str(e)}"}

            logger.info(f"Preview complete: {total_files} files, {skipped} skipped, {len(groups)} groups")

            return {
                "groups": groups,
                "total_files": total_files,
                "total_size_mb": round(total_size / 1_048_576, 2),
                "skipped": skipped,
            }

        except Exception as e:
            logger.error(f"Unexpected error in preview_folder: {str(e)}", exc_info=True)
            return {"error": f"Preview failed: {str(e)}"}

    def organize(self, folder_path: str):
        """
        Run the full organization. Runs in a background thread and pushes
        progress events to the frontend via window.__bridge().
        """
        try:
            if not folder_path:
                return {"error": "Folder path is required"}

            if not os.path.exists(folder_path):
                return {"error": "Folder does not exist"}

            if not os.path.isdir(folder_path):
                return {"error": "Path is not a directory"}

            logger.info(f"Starting organization of folder: {folder_path}")

        except Exception as e:
            logger.error(f"Error validating folder: {str(e)}")
            return {"error": f"Validation failed: {str(e)}"}

        def _run():
            try:
                logger.info("Organization thread started")
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
                    except PermissionError as e:
                        logger.warning(f"Permission denied moving {fname}: {e}")
                        skipped += 1
                    except shutil.Error as e:
                        logger.warning(f"Shutil error moving {fname}: {e}")
                        skipped += 1
                    except Exception as e:
                        logger.warning(f"Unexpected error moving {fname}: {e}")
                        skipped += 1

                    self._push("progress", {
                        "current": i + 1, "total": total,
                        "file": fname, "pct": round((i + 1) / max(total, 1) * 100),
                    })

                # Save log
                if moved > 0:
                    try:
                        log_path = os.path.join(get_app_dir(), "operation_log.json")
                        logs = []
                        if os.path.exists(log_path):
                            try:
                                with open(log_path) as f:
                                    logs = json.load(f)
                            except Exception as e:
                                logger.warning(f"Could not read existing log file: {e}")

                        logs.append(log)

                        with open(log_path, "w") as f:
                            json.dump(logs, f, indent=2)

                        logger.info(f"Operation log saved: {moved} files moved")
                    except Exception as e:
                        logger.error(f"Failed to save operation log: {e}")

                logger.info(f"Organization complete: {moved} moved, {renamed} renamed, {skipped} skipped, {total_size / 1_048_576:.2f} MB")

                self._push("done", {
                    "moved": moved, "renamed": renamed,
                    "skipped": skipped,
                    "size_mb": round(total_size / 1_048_576, 2),
                    "master_folder": self._settings["master_folder_name"],
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "can_undo": moved > 0,
                })

            except Exception as e:
                logger.error(f"Error during organization: {str(e)}", exc_info=True)
                self._push("error", {"message": str(e)})

        threading.Thread(target=_run, daemon=True).start()
        return {"status": "started"}

    def undo(self):
        """Restore files from the last operation log entry."""
        try:
            log_path = os.path.join(get_app_dir(), "operation_log.json")

            if not os.path.exists(log_path):
                logger.warning("Undo called but no log file exists")
                return {"error": "No operations to undo"}

            try:
                with open(log_path) as f:
                    logs = json.load(f)
            except Exception as e:
                logger.error(f"Could not read operation log: {e}")
                return {"error": "Could not read operation log"}

            if not logs:
                logger.warning("Undo called but log is empty")
                return {"error": "No operations to undo"}

            last = logs[-1]
            logger.info(f"Starting undo of operation from {last.get('timestamp', 'unknown time')}")

            restored = failed = 0
            for item in last.get("files", []):
                try:
                    if os.path.exists(item["new_path"]):
                        os.makedirs(os.path.dirname(item["original_path"]), exist_ok=True)
                        shutil.move(item["new_path"], item["original_path"])
                        restored += 1
                    else:
                        logger.warning(f"File not found for undo: {item['new_path']}")
                        failed += 1
                except PermissionError as e:
                    logger.error(f"Permission denied restoring file: {e}")
                    failed += 1
                except Exception as e:
                    logger.error(f"Error restoring file: {e}")
                    failed += 1

            logs.pop()
            with open(log_path, "w") as f:
                json.dump(logs, f, indent=2)

            logger.info(f"Undo complete: {restored} restored, {failed} failed")

            return {
                "restored": restored,
                "failed": failed,
                "has_more": len(logs) > 0,
            }

        except Exception as e:
            logger.error(f"Unexpected error in undo: {str(e)}", exc_info=True)
            return {"error": f"Undo failed: {str(e)}"}

    def get_operation_logs(self):
        """Return the operation history for the Statistics screen."""
        try:
            log_path = os.path.join(get_app_dir(), "operation_log.json")
            if not os.path.exists(log_path):
                logger.info("No operation logs found")
                return []

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

            logger.info(f"Returned {len(result)} operation logs")
            return result

        except Exception as e:
            logger.error(f"Error getting operation logs: {str(e)}")
            return []

    def get_category_stats(self):
        """
        Get breakdown of files organized by category across all operations.
        Returns category counts, sizes, and percentages for visualization.
        """
        try:
            log_path = os.path.join(get_app_dir(), "operation_log.json")
            if not os.path.exists(log_path):
                return {"categories": {}, "total_files": 0, "total_size": 0}

            ext_map = _load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))

            with open(log_path) as f:
                logs = json.load(f)

            category_data = {}
            total_files = 0
            total_size = 0

            for log in logs:
                for item in log.get("files", []):
                    # Extract file extension and map to category
                    fname = os.path.basename(item.get("new_path", ""))
                    ext = Path(fname).suffix.lstrip(".").upper()

                    if ext:
                        dest = ext_map.get(ext, f"Other/{ext}")
                        category = dest.split("/")[0]

                        if category not in category_data:
                            category_data[category] = {
                                "count": 0,
                                "size": 0,
                            }

                        category_data[category]["count"] += 1
                        category_data[category]["size"] += item.get("size", 0)
                        total_files += 1
                        total_size += item.get("size", 0)

            # Calculate percentages and format sizes
            for category in category_data:
                cat = category_data[category]
                cat["percentage"] = round((cat["count"] / total_files * 100), 1) if total_files > 0 else 0
                cat["size_mb"] = round(cat["size"] / 1_048_576, 2)

            # Sort by count descending
            sorted_categories = dict(sorted(category_data.items(), key=lambda x: x[1]["count"], reverse=True))

            logger.info(f"Category stats: {len(sorted_categories)} categories, {total_files} total files")

            return {
                "categories": sorted_categories,
                "total_files": total_files,
                "total_size_mb": round(total_size / 1_048_576, 2),
            }

        except Exception as e:
            logger.error(f"Error getting category stats: {str(e)}", exc_info=True)
            return {"categories": {}, "total_files": 0, "total_size_mb": 0}

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
