"""
FileType Organizer Pro — PyQt6 Implementation
=============================================
Install deps:
    pip install PyQt6
Run:
    python pyqt6_app.py
"""
import os
import sys
import shutil
import threading
import json
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QFileDialog, QMessageBox,
    QProgressBar, QDialog, QScrollArea, QTextEdit, QTabWidget,
    QLineEdit, QRadioButton, QCheckBox, QButtonGroup, QGridLayout,
    QSizePolicy, QTreeWidget, QTreeWidgetItem,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QMimeData, QSize,
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QDragEnterEvent, QDropEvent, QIcon,
    QPainter, QBrush, QPen, QLinearGradient,
)
# ── Colour tokens ─────────────────────────────────────────────
BG        = "#f8f8f5"
SURFACE   = "#ffffff"
SURFACE2  = "#f2f2ef"
BORDER    = "#e4e4dc"
TXT1      = "#1a1a17"
TXT2      = "#5c5c56"
TXT3      = "#9b9b93"
ACCENT    = "#1a6cf0"
ACC_LIGHT = "#e8f0fe"
GREEN     = "#16a34a"
GREEN_L   = "#dcfce7"
AMBER     = "#d97706"
RED       = "#dc2626"
def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
# ── Global stylesheet ─────────────────────────────────────────
APP_QSS = f"""
QWidget {{
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    font-size: 13px;
    color: {TXT1};
    background-color: {BG};
}}
QMainWindow, QDialog {{
    background-color: {BG};
}}
/* Flat push button — secondary style */
QPushButton {{
    background-color: {SURFACE};
    color: {TXT2};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {SURFACE2};
}}
QPushButton:disabled {{
    color: {TXT3};
    background-color: {SURFACE};
}}
/* Primary button */
QPushButton#primary {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 9px 24px;
    font-weight: 700;
}}
QPushButton#primary:hover {{
    background-color: #1459d0;
}}
QPushButton#primary:disabled {{
    background-color: #99b8f5;
}}
/* Danger button */
QPushButton#danger {{
    background-color: {RED};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 700;
}}
QPushButton#danger:hover {{
    background-color: #b91c1c;
}}
/* Card frames */
QFrame#card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
/* Drop zone */
QFrame#dropzone {{
    background-color: {SURFACE};
    border: 2px dashed {BORDER};
    border-radius: 14px;
}}
QFrame#dropzone[drag=true] {{
    background-color: {ACC_LIGHT};
    border-color: {ACCENT};
}}
/* Progress bar */
QProgressBar {{
    background-color: {SURFACE2};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 3px;
}}
/* Nav frame */
QFrame#nav {{
    background-color: {SURFACE};
    border-bottom: 1px solid {BORDER};
}}
/* Scroll area */
QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}
/* Tab widget */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 12px;
    background-color: {SURFACE};
}}
QTabBar::tab {{
    padding: 8px 18px;
    color: {TXT2};
    font-weight: 500;
    background-color: transparent;
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    font-weight: 700;
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{
    color: {TXT1};
}}
/* Text edit / input */
QTextEdit, QLineEdit {{
    background-color: {SURFACE2};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TXT1};
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 12px;
}}
QTextEdit:focus, QLineEdit:focus {{
    border-color: {ACCENT};
    background-color: {SURFACE};
}}
/* Tree widget */
QTreeWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    outline: none;
}}
QTreeWidget::item {{
    padding: 4px 8px;
    border-radius: 6px;
}}
QTreeWidget::item:hover {{
    background-color: {SURFACE2};
}}
QTreeWidget::item:selected {{
    background-color: {ACC_LIGHT};
    color: {ACCENT};
}}
/* Radio / Check */
QRadioButton, QCheckBox {{
    color: {TXT2};
    font-size: 13px;
    spacing: 8px;
}}
QRadioButton::indicator, QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {BORDER};
    border-radius: 8px;
    background: {SURFACE};
}}
QRadioButton::indicator:checked, QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
"""
# ── Extension map ──────────────────────────────────────────────
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
JPG=Images/JPG Images
JPEG=Images/JPG Images
PNG=Images/PNG Images
GIF=Images/GIF Images
WEBP=Images/WebP Images
HEIC=Images/HEIC Images
SVG=Images/SVG Images
MP4=Videos/MP4 Videos
MKV=Videos/MKV Videos
MOV=Videos/MOV Videos
AVI=Videos/AVI Videos
MP3=Audio/MP3 Audio
WAV=Audio/WAV Audio
FLAC=Audio/FLAC Audio
AAC=Audio/AAC Audio
ZIP=Archives/ZIP Archives
RAR=Archives/RAR Archives
7Z=Archives/7Z Archives
TAR=Archives/TAR Archives
GZ=Archives/GZ Archives
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
EXE=Applications/Windows
DMG=Applications/Mac
APK=Applications/Android
TTF=Fonts/TrueType
OTF=Fonts/OpenType
WOFF=Fonts/Web
WOFF2=Fonts/Web
"""
def ensure_ext_map(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_EXT_MAP)
def load_ext_map(path):
    ensure_ext_map(path)
    m = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            ext, folder = line.split("=", 1)
            m[ext.strip().upper()] = folder.strip()
    return m
def unique_name(dest, fname):
    if not os.path.exists(os.path.join(dest, fname)):
        return fname
    name, ext = os.path.splitext(fname)
    i = 1
    while os.path.exists(os.path.join(dest, f"{name}_{i}{ext}")):
        i += 1
    return f"{name}_{i}{ext}"
# ══════════════════════════════════════════════════════════════
#  Worker thread
# ══════════════════════════════════════════════════════════════
class OrganizerWorker(QThread):
    progress   = pyqtSignal(int, int)   # current, total
    finished   = pyqtSignal(dict)       # stats
    error      = pyqtSignal(str)
    def __init__(self, folder, settings):
        super().__init__()
        self.folder   = folder
        self.settings = settings
    def run(self):
        try:
            ext_map = load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
            moved = renamed = skipped = 0
            total_size = 0
            log = {"timestamp": datetime.now().isoformat(),
                   "source_folder": self.folder, "files": []}
            entries = []
            if self.settings.get("recursive"):
                for root, _, files in os.walk(self.folder):
                    if self.settings.get("master_folder_name", "") in root:
                        continue
                    for f in files:
                        entries.append(os.path.join(root, f))
            else:
                for f in os.listdir(self.folder):
                    p = os.path.join(self.folder, f)
                    if os.path.isfile(p):
                        entries.append(p)
            total = len(entries)
            for i, fpath in enumerate(entries):
                fname = os.path.basename(fpath)
                if any(p in fname for p in self.settings.get("exclude_patterns", [])):
                    skipped += 1
                    self.progress.emit(i + 1, total)
                    continue
                ext = Path(fname).suffix.lstrip(".").upper()
                if not ext:
                    skipped += 1
                    self.progress.emit(i + 1, total)
                    continue
                master = os.path.join(self.folder, self.settings.get("master_folder_name", "Organised Files - FTO"))
                dest_dir = os.path.join(master, ext_map.get(ext, f"Other/{ext}"))
                os.makedirs(dest_dir, exist_ok=True)
                dest_name = fname
                dup_mode = self.settings.get("handle_duplicates", "rename")
                if os.path.exists(os.path.join(dest_dir, fname)):
                    if dup_mode == "rename":
                        dest_name = unique_name(dest_dir, fname)
                        renamed += 1
                    elif dup_mode == "skip":
                        skipped += 1
                        self.progress.emit(i + 1, total)
                        continue
                dest_path = os.path.join(dest_dir, dest_name)
                try:
                    size = os.path.getsize(fpath)
                    shutil.move(fpath, dest_path)
                    log["files"].append({"original_path": fpath, "new_path": dest_path, "size": size})
                    moved += 1
                    total_size += size
                except Exception:
                    skipped += 1
                self.progress.emit(i + 1, total)
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
            self.finished.emit({"moved": moved, "renamed": renamed,
                                "skipped": skipped, "size": total_size, "log": log})
        except Exception as e:
            self.error.emit(str(e))
# ══════════════════════════════════════════════════════════════
#  Drop Zone widget
# ══════════════════════════════════════════════════════════════
class DropZone(QFrame):
    folderDropped = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self._build()
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)
        self._icon = QLabel("↑")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setFont(QFont("Segoe UI", 26))
        self._icon.setStyleSheet(f"color: {TXT3}; border: none;")
        layout.addWidget(self._icon)
        self._title = QLabel("Drop a folder here")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self._title.setStyleSheet(f"color: {TXT1}; border: none;")
        layout.addWidget(self._title)
        sub = QLabel("or browse your computer")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {TXT3}; border: none;")
        layout.addWidget(sub)
        browse = QPushButton("Browse folder")
        browse.setFixedWidth(130)
        browse.clicked.connect(self._browse)
        browse.setStyleSheet(f"""
            QPushButton {{
                background: {SURFACE}; color: {TXT2};
                border: 1px solid {BORDER}; border-radius: 8px;
                padding: 7px 16px; font-weight: 600; font-size: 12px;
            }}
            QPushButton:hover {{ background: {SURFACE2}; }}
        """)
        layout.addWidget(browse, alignment=Qt.AlignmentFlag.AlignCenter)
    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to organize")
        if folder:
            self.folderDropped.emit(folder)
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("drag", "true")
            self.setStyleSheet(f"""
                QFrame#dropzone {{
                    background-color: {ACC_LIGHT};
                    border: 2px dashed {ACCENT};
                    border-radius: 14px;
                }}
            """)
            self._title.setStyleSheet(f"color: {ACCENT}; border: none; font-weight: 700;")
            self._title.setText("Drop folder here!")
    def dragLeaveEvent(self, event):
        self._reset_style()
    def dropEvent(self, event: QDropEvent):
        self._reset_style()
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.folderDropped.emit(path)
            else:
                QMessageBox.warning(self, "Invalid Drop", "Please drop a folder, not a file.")
    def _reset_style(self):
        self.setStyleSheet("")  # revert to global QSS
        self._title.setStyleSheet(f"color: {TXT1}; border: none; font-weight: 700;")
        self._title.setText("Drop a folder here")
# ══════════════════════════════════════════════════════════════
#  Main Window
# ══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_folder = None
        self.worker = None
        self.settings = self._load_settings()
        self._build_ui()
        self.setWindowTitle("FileType Organizer Pro")
        self.resize(760, 600)
        self._centre()
    def _centre(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    # ── Settings ──────────────────────────────────────────────
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
    def _save_settings(self):
        path = os.path.join(get_app_dir(), "settings.json")
        with open(path, "w") as f:
            json.dump(self.settings, f, indent=2)
    # ── UI ────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget()
        root.setStyleSheet(f"background-color: {BG};")
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        # Nav
        nav = QFrame()
        nav.setObjectName("nav")
        nav.setFixedHeight(52)
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(20, 0, 20, 0)
        logo_box = QFrame()
        logo_box.setFixedSize(28, 28)
        logo_box.setStyleSheet(f"background: {ACCENT}; border-radius: 7px;")
        nav_layout.addWidget(logo_box)
        title_lbl = QLabel("FileType Organizer")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {TXT1}; background: transparent;")
        nav_layout.addWidget(title_lbl)
        pro_lbl = QLabel("Pro")
        pro_lbl.setFixedSize(34, 20)
        pro_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pro_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        pro_lbl.setStyleSheet(f"color: {ACCENT}; background: {ACC_LIGHT}; border-radius: 99px;")
        nav_layout.addWidget(pro_lbl)
        nav_layout.addStretch()
        credit = QLabel("by Kahilu Chipango")
        credit.setStyleSheet(f"color: {TXT3}; background: transparent; font-size: 11px;")
        nav_layout.addWidget(credit)
        vbox.addWidget(nav)
        # Content
        content = QWidget()
        content.setStyleSheet(f"background-color: {BG};")
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(28, 24, 28, 24)
        c_layout.setSpacing(16)
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.folderDropped.connect(self._set_folder)
        c_layout.addWidget(self.drop_zone)
        # Folder info strip
        info_card = QFrame()
        info_card.setObjectName("card")
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(16, 12, 16, 12)
        self.folder_lbl = QLabel("No folder selected")
        self.folder_lbl.setStyleSheet(f"color: {TXT3}; border: none; font-size: 13px;")
        self.folder_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        info_layout.addWidget(self.folder_lbl)
        self.status_badge = QLabel("")
        self.status_badge.setFixedSize(60, 22)
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.status_badge.setStyleSheet(f"color: {GREEN}; background: {GREEN_L}; border-radius: 99px; border: none;")
        info_layout.addWidget(self.status_badge)
        c_layout.addWidget(info_card)
        # Quick stats
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        self.stat_labels = []
        for i, (cat, icon) in enumerate([("Images", "🖼"), ("Documents", "📄"), ("Videos", "🎬")]):
            card = QFrame()
            card.setObjectName("card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(14, 14, 14, 14)
            cl.setSpacing(4)
            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI", 18))
            icon_lbl.setStyleSheet("border: none;")
            cl.addWidget(icon_lbl)
            count_lbl = QLabel("—")
            count_lbl.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            count_lbl.setStyleSheet(f"color: {TXT1}; border: none;")
            cl.addWidget(count_lbl)
            cat_lbl = QLabel(cat)
            cat_lbl.setStyleSheet(f"color: {TXT3}; font-size: 11px; border: none;")
            cl.addWidget(cat_lbl)
            stats_grid.addWidget(card, 0, i)
            self.stat_labels.append(count_lbl)
        c_layout.addLayout(stats_grid)
        # Progress
        self.prog_text = QLabel("Ready to organize files")
        self.prog_text.setStyleSheet(f"color: {TXT3}; font-size: 12px;")
        c_layout.addWidget(self.prog_text)
        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(6)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setValue(0)
        c_layout.addWidget(self.prog_bar)
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.preview_btn = QPushButton("👁  Preview")
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self._preview)
        btn_row.addWidget(self.preview_btn)
        self.undo_btn = QPushButton("↩  Undo")
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._undo)
        btn_row.addWidget(self.undo_btn)
        settings_btn = QPushButton("⚙  Settings")
        settings_btn.clicked.connect(self._open_settings)
        btn_row.addWidget(settings_btn)
        btn_row.addStretch()
        self.org_btn = QPushButton("Organize Now →")
        self.org_btn.setObjectName("primary")
        self.org_btn.setEnabled(False)
        self.org_btn.clicked.connect(self._organize)
        btn_row.addWidget(self.org_btn)
        c_layout.addLayout(btn_row)
        vbox.addWidget(content)
    # ── Folder selection ──────────────────────────────────────
    def _set_folder(self, path):
        self.selected_folder = path
        display = path if len(path) <= 65 else "…" + path[-62:]
        self.folder_lbl.setText(display)
        self.folder_lbl.setStyleSheet(f"color: {ACCENT}; border: none; font-size: 13px; font-weight: 600;")
        self.status_badge.setText("Ready")
        self.org_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.prog_text.setText("Folder selected — ready to organize!")
        self.prog_text.setStyleSheet(f"color: {TXT2}; font-size: 12px;")
        self.prog_bar.setValue(0)
        self._scan_counts()
    def _scan_counts(self):
        if not self.selected_folder:
            return
        counts = [0, 0, 0]
        img = {"JPG","JPEG","PNG","GIF","WEBP","HEIC","SVG","BMP"}
        doc = {"PDF","DOC","DOCX","TXT","XLS","XLSX","PPT","PPTX","MD","CSV"}
        vid = {"MP4","MKV","MOV","AVI","WEBM","FLV"}
        try:
            for f in os.listdir(self.selected_folder):
                ext = Path(f).suffix.lstrip(".").upper()
                if ext in img: counts[0] += 1
                elif ext in doc: counts[1] += 1
                elif ext in vid: counts[2] += 1
        except Exception:
            pass
        for lbl, c in zip(self.stat_labels, counts):
            lbl.setText(str(c))
    # ── Organize ──────────────────────────────────────────────
    def _organize(self):
        if not self.selected_folder:
            return
        self.org_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)
        self.prog_bar.setMaximum(0)  # indeterminate
        self.prog_text.setText("Organizing files…")
        self.prog_text.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: 600;")
        self.worker = OrganizerWorker(self.selected_folder, self.settings)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    def _on_progress(self, current, total):
        if self.prog_bar.maximum() == 0 and total > 0:
            self.prog_bar.setMaximum(total)
        self.prog_bar.setValue(current)
    def _on_finished(self, stats):
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(100)
        self.org_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        if stats["moved"] > 0:
            self.undo_btn.setEnabled(True)
        size_mb = stats["size"] / 1_048_576
        self.prog_text.setText(f"✓ Complete! {stats['moved']} files organized({size_mb:.1f} MB)")
        self.prog_text.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: 600;")
        msg = (f"Organization complete!\n\n"
               f"Files moved:    {stats['moved']}\n"
               f"Renamed (dupes): {stats['renamed']}\n"
               f"Skipped:        {stats['skipped']}\n"
               f"Total size:     {size_mb:.2f} MB\n"
               f"Completed at:   {datetime.now().strftime('%H:%M:%S')}")
        QMessageBox.information(self, "Done", msg)
    def _on_error(self, msg):
        self.prog_bar.setMaximum(100)
        self.prog_bar.setValue(0)
        self.org_btn.setEnabled(True)
        self.preview_btn.setEnabled(True)
        self.prog_text.setText("An error occurred — please try again")
        self.prog_text.setStyleSheet(f"color: {RED}; font-size: 12px;")
        QMessageBox.critical(self, "Error", msg)
    # ── Preview ───────────────────────────────────────────────
    def _preview(self):
        if not self.selected_folder:
            return
        ext_map = load_ext_map(os.path.join(get_app_dir(), "extension_map.txt"))
        groups: dict[str, list] = {}
        total_size = 0
        try:
            for fname in os.listdir(self.selected_folder):
                fpath = os.path.join(self.selected_folder, fname)
                if not os.path.isfile(fpath):
                    continue
                if any(p in fname for p in self.settings.get("exclude_patterns", [])):
                    continue
                ext = Path(fname).suffix.lstrip(".").upper()
                if not ext:
                    continue
                folder = ext_map.get(ext, f"Other/{ext}")
                groups.setdefault(folder, []).append(fname)
                total_size += os.path.getsize(fpath)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Preview — Planned Changes")
        dlg.resize(640, 520)
        dlg.setStyleSheet(f"background: {BG};")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)
        title = QLabel("Preview Changes")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TXT1};")
        layout.addWidget(title)
        total_files = sum(len(v) for v in groups.values())
        sub = QLabel(f"{total_files} files · {total_size/1_048_576:.1f} MB")
        sub.setStyleSheet(f"color: {TXT3}; font-size: 12px;")
        layout.addWidget(sub)
        tree = QTreeWidget()
        tree.setHeaderLabels(["Destination folder", "Files"])
        tree.setColumnWidth(0, 440)
        tree.setStyleSheet(APP_QSS)
        for folder, files in sorted(groups.items()):
            item = QTreeWidgetItem([f"📁  {folder}", str(len(files))])
            item.setFont(0, QFont("Segoe UI", 12, QFont.Weight.Bold))
            for f in sorted(files)[:10]:
                child = QTreeWidgetItem([f"    {f}", ""])
                child.setForeground(0, QColor(TXT3))
                item.addChild(child)
            if len(files) > 10:
                more = QTreeWidgetItem([f"    … and {len(files)-10} more", ""])
                more.setForeground(0, QColor(TXT3))
                item.addChild(more)
            tree.addTopLevelItem(item)
        tree.expandItem(tree.topLevelItem(0))
        layout.addWidget(tree)
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(cancel_btn)
        proceed_btn = QPushButton("Organize Now →")
        proceed_btn.setObjectName("primary")
        proceed_btn.setStyleSheet(f"QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 10px; padding: 9px 20px; font-weight: 700; }} QPushButton:hover {{ background: #1459d0; }}")
        proceed_btn.clicked.connect(lambda: [dlg.accept(), self._organize()])
        btn_row.addWidget(proceed_btn)
        layout.addLayout(btn_row)
        dlg.exec()
    # ── Undo ──────────────────────────────────────────────────
    def _undo(self):
        log_path = os.path.join(get_app_dir(), "operation_log.json")
        if not os.path.exists(log_path):
            QMessageBox.information(self, "Undo", "No operations to undo.")
            return
        with open(log_path) as f:
            logs = json.load(f)
        if not logs:
            QMessageBox.information(self, "Undo", "No operations to undo.")
            return
        last = logs[-1]
        reply = QMessageBox.question(self, "Confirm Undo",
                                     f"Undo operation from {last['timestamp']}?\n"
                                     f"{len(last['files'])} files will be moved back.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        for item in last["files"]:
            try:
                if os.path.exists(item["new_path"]):
                    os.makedirs(os.path.dirname(item["original_path"]), exist_ok=True)
                    shutil.move(item["new_path"], item["original_path"])
            except Exception:
                pass
        logs.pop()
        with open(log_path, "w") as f:
            json.dump(logs, f, indent=2)
        if not logs:
            self.undo_btn.setEnabled(False)
        self.prog_text.setText("✓ Undo complete — files restored")
        self.prog_text.setStyleSheet(f"color: {GREEN}; font-size: 12px; font-weight: 600;")
        QMessageBox.information(self, "Undo Complete", "Files have been restored to their original locations.")
    # ── Settings ──────────────────────────────────────────────
    def _open_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.resize(620, 540)
        dlg.setStyleSheet(f"background: {BG};")
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(14)
        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TXT1};")
        layout.addWidget(title)
        tabs = QTabWidget()
        tabs.setStyleSheet(APP_QSS)
        # ── General ───────────────────────────────────────────
        general = QWidget()
        gl = QVBoxLayout(general)
        gl.setContentsMargins(16, 16, 16, 16)
        gl.setSpacing(14)
        gl.addWidget(QLabel("Master folder name:"))
        master_entry = QLineEdit(self.settings.get("master_folder_name", "Organised Files - FTO"))
        gl.addWidget(master_entry)
        gl.addWidget(QLabel("Duplicate handling:"))
        dup_group = QButtonGroup(dlg)
        dup_val = self.settings.get("handle_duplicates", "rename")
        for val, lbl in [("rename", "Rename (add _1, _2…)"),
                          ("skip", "Skip duplicates"),
                          ("overwrite", "Overwrite existing")]:
            rb = QRadioButton(lbl)
            rb.setProperty("value", val)
            if val == dup_val:
                rb.setChecked(True)
            dup_group.addButton(rb)
            gl.addWidget(rb)
        recursive_cb = QCheckBox("Recursive organization")
        recursive_cb.setChecked(self.settings.get("recursive", False))
        gl.addWidget(recursive_cb)
        auto_cb = QCheckBox("Auto-organize(every 30s)")
        auto_cb.setChecked(self.settings.get("auto_organize", False))
        gl.addWidget(auto_cb)
        gl.addStretch()
        tabs.addTab(general, "General")
        # ── Patterns ──────────────────────────────────────────
        pat_widget = QWidget()
        pl = QVBoxLayout(pat_widget)
        pl.setContentsMargins(16, 16, 16, 16)
        pl.addWidget(QLabel("One pattern per line:"))
        patterns_box = QTextEdit()
        patterns_box.setPlainText("\n".join(self.settings.get("exclude_patterns", [])))
        pl.addWidget(patterns_box)
        tabs.addTab(pat_widget, "Exclude Patterns")
        # ── Ext map ───────────────────────────────────────────
        map_widget = QWidget()
        ml = QVBoxLayout(map_widget)
        ml.setContentsMargins(16, 16, 16, 16)
        ml.addWidget(QLabel("Format: EXTENSION=Category/Subfolder"))
        ext_path = os.path.join(get_app_dir(), "extension_map.txt")
        ensure_ext_map(ext_path)
        with open(ext_path) as f:
            ext_content = f.read()
        map_box = QTextEdit()
        map_box.setPlainText(ext_content)
        ml.addWidget(map_box)
        tabs.addTab(map_widget, "Extension Map")
        layout.addWidget(tabs)
        # Save / Cancel
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dlg.reject)
        btn_row.addWidget(cancel_btn)
        def save():
            self.settings["master_folder_name"] = master_entry.text().strip() or "Organised Files - FTO"
            checked = dup_group.checkedButton()
            if checked:
                self.settings["handle_duplicates"] = checked.property("value")
            self.settings["recursive"] = recursive_cb.isChecked()
            self.settings["auto_organize"] = auto_cb.isChecked()
            self.settings["exclude_patterns"] = [
                l.strip() for l in patterns_box.toPlainText().splitlines() if l.strip()
            ]
            self._save_settings()
            with open(ext_path, "w") as f:
                f.write(map_box.toPlainText())
            dlg.accept()
        save_btn = QPushButton("Save changes")
        save_btn.setObjectName("primary")
        save_btn.setStyleSheet(f"QPushButton {{ background: {ACCENT}; color: white; border: none; border-radius: 10px; padding: 9px 20px; font-weight: 700; }} QPushButton:hover {{ background: #1459d0; }}")
        save_btn.clicked.connect(save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)
        dlg.exec()
# ── Entry point ───────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()