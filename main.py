import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import threading
from datetime import datetime
import json
import time
import re
from pathlib import Path
# Add import for drag and drop


try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Get the directory where the script or exe is located
def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Default extension map content
DEFAULT_EXTENSION_MAP = """
PDF=Documents/PDF Files
DOC=Documents/Word Files
DOCX=Documents/Word Files
TXT=Documents/Text Files
XLS=Documents/Excel Files
XLSX=Documents/Excel Files
XLSB=Documents/Excel Files
PPT=Documents/PowerPoint Files
PPTX=Documents/PowerPoint Files
ODT=Documents/OpenDocument Files
ODS=Documents/OpenDocument Files
CSV=Documents/CSV Files
RTF=Documents/Text Files
MD=Documents/Markdown Files
LOG=Documents/Log Files
EPUB=Documents/eBooks
MOBI=Documents/eBooks
CBZ=Documents/Comic Books
CBR=Documents/Comic Books

JPG=Images/JPG Images
JPEG=Images/JPG Images
PNG=Images/PNG Images
GIF=Images/GIF Images
BMP=Images/BMP Images
SVG=Images/SVG Images
WEBP=Images/WEBP Images
TIFF=Images/TIFF Images
ICO=Images/Icon Files
HEIC=Images/HEIC Images
RAW=Images/RAW Images
CR2=Images/RAW Images
NEF=Images/RAW Images
ARW=Images/RAW Images
DNG=Images/RAW Images

MP4=Videos/MP4 Videos
MKV=Videos/MKV Videos
AVI=Videos/AVI Videos
MOV=Videos/MOV Videos
WMV=Videos/WMV Videos
FLV=Videos/FLV Videos
WEBM=Videos/WEBM Videos
MPEG=Videos/MPEG Videos
MPG=Videos/MPEG Videos
3GP=Videos/3GP Videos
M4V=Videos/M4V Videos
TS=Videos/TS Videos
VOB=Videos/VOB Videos
OGV=Videos/OGV Videos
F4V=Videos/F4V Videos

MP3=Audio/MP3 Audio
WAV=Audio/WAV Audio
AAC=Audio/AAC Audio
FLAC=Audio/FLAC Audio
OGG=Audio/OGG Audio
M4A=Audio/M4A Audio
WMA=Audio/WMA Audio
AMR=Audio/AMR Audio
AIF=Audio/AIF Audio
AIFF=Audio/AIF Audio
APE=Audio/APE Audio
OPUS=Audio/OPUS Audio
MID=Audio/MIDI Audio
MIDI=Audio/MIDI Audio

ZIP=Archives/ZIP Archives
RAR=Archives/RAR Archives
7Z=Archives/7Z Archives
TAR=Archives/TAR Archives
GZ=Archives/GZ Archives
BZ2=Archives/BZ2 Archives
XZ=Archives/XZ Archives
ISO=Archives/ISO Archives
CAB=Archives/CAB Archives
ARJ=Archives/ARJ Archives
LZH=Archives/LZH Archives
ACE=Archives/ACE Archives
Z=Archives/Z Archives
JAR=Archives/JAR Archives

PY=Code/Python
JS=Code/JavaScript
JAVA=Code/Java
CPP=Code/C++
C=Code/C
CS=Code/CSharp
HTML=Code/HTML
CSS=Code/CSS
PHP=Code/PHP
RB=Code/Ruby
GO=Code/Go
RS=Code/Rust
TS=Code/TypeScript
SH=Code/Shell
BAT=Code/Batch
PL=Code/Perl
SWIFT=Code/Swift
KOTLIN=Code/Kotlin
SCALA=Code/Scala
R=Code/R
IPYNB=Code/Jupyter
JSON=Code/JSON
XML=Code/XML
YML=Code/YAML
YAML=Code/YAML
ASP=Code/ASP
ASPX=Code/ASP.NET
VBS=Code/VBScript
SQL=Code/SQL
LUA=Code/Lua
H=Code/C-Headers
HPP=Code/C++-Headers

EXE=Applications/Windows Executables
MSI=Applications/Windows Installers
APK=Applications/Android Packages
APPX=Applications/Windows App Packages
DMG=Applications/Mac Installers
PKG=Applications/Mac Packages
APP=Applications/Mac Apps
IPA=Applications/iOS Apps

TTF=Fonts/TrueType
OTF=Fonts/OpenType
FON=Fonts/Bitmap
WOFF=Fonts/Web Open Font
WOFF2=Fonts/Web Open Font 2
EOT=Fonts/Embedded OpenType
PFA=Fonts/PostScript
PFB=Fonts/PostScript

KEY=Presentations/Keynote
ODP=Presentations/OpenDocument
NUMBERS=Spreadsheets/Numbers
XLSM=Spreadsheets/Excel Macro

AI=VectorGraphics/Illustrator
EPS=VectorGraphics/EPS
CDR=VectorGraphics/CorelDRAW
PSD=VectorGraphics/Photoshop
SVGZ=VectorGraphics/SVG Compressed
SVGZ=VectorGraphics/SVG Compressed
SVG=VectorGraphics/SVG
PDF=VectorGraphics/PDF


# Add more extensions as needed
# You can add more extensions and their corresponding folders here
# Example:
# TXT=Documents/Text Files
# TXT=Documents/Text Files
# MP3=Audio/MP3 Audio
# 
"""

def ensure_extension_map(filepath):
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(DEFAULT_EXTENSION_MAP)

def load_extension_map(filepath):
    ext_map = {}
    ensure_extension_map(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                ext, folder = line.split("=", 1)
                ext_map[ext.strip().upper()] = folder.strip()
    return ext_map

def get_unique_filename(dest_folder, filename):
    """Generate unique filename if file already exists"""
    if not os.path.exists(os.path.join(dest_folder, filename)):
        return filename

    name, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(os.path.join(dest_folder, f"{name}_{counter}{ext}")):
        counter += 1
    return f"{name}_{counter}{ext}"

def save_operation_log(log_path, operation_data):
    """Save organization operation to log file for undo"""
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(operation_data)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2)

def load_operation_logs(log_path):
    """Load operation logs for undo"""
    if not os.path.exists(log_path):
        return []
    with open(log_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

class ModernFolderOrganizer:
    def __init__(self):
        # Use TkinterDnD.Tk if available, else fallback to tk.Tk
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()

        # Initialize settings
        self.settings = self.load_settings()
        self.last_operation = None
        self.auto_organize_job = None
        self.last_check_time = time.time()

        self.setup_window()
        self.create_widgets()
        self.setup_styles()

        # Start auto-organize if enabled
        if self.settings.get("auto_organize", False) and self.selected_folder:
            self.start_auto_organize()

    def load_settings(self):
        """Load user settings from config file"""
        app_dir = get_app_dir()
        settings_path = os.path.join(app_dir, "settings.json")
        default_settings = {
            "master_folder_name": "Organised Files - FTO",
            "exclude_patterns": [".DS_Store", "Thumbs.db", "desktop.ini", ".git", ".gitignore"],
            "handle_duplicates": "rename",  # rename, skip, overwrite
            "recursive": False,
            "auto_organize": False,
            "rules": []  # For date/size rules
        }

        if not os.path.exists(settings_path):
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
            return default_settings

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with defaults for new settings
                default_settings.update(loaded)
                return default_settings
        except:
            return default_settings

    def save_settings(self):
        """Save settings to config file"""
        app_dir = get_app_dir()
        settings_path = os.path.join(app_dir, "settings.json")
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2)
        
    def setup_window(self):
        self.root.title("✨ Modern Folder Organizer")
        self.root.geometry("650x550")  # Increased height for better button visibility
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)

        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.root.winfo_screenheight() // 2) - (550 // 2)
        self.root.geometry(f"650x550+{x}+{y}")
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles for modern look
        style.configure('Modern.TButton',
                       background='#4a9eff',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 15))
        
        style.map('Modern.TButton',
                 background=[('active', '#357abd'),
                           ('pressed', '#2968a3')])
        
        style.configure('Secondary.TButton',
                       background='#6c757d',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 10))
        
        style.map('Secondary.TButton',
                 background=[('active', '#545b62'),
                           ('pressed', '#495057')])
        
        style.configure('TProgressbar',
                       background='#4a9eff',
                       troughcolor='#2d2d2d',
                       borderwidth=0,
                       lightcolor='#4a9eff',
                       darkcolor='#4a9eff')
        
    def create_widgets(self):
        # Main container with gradient effect
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=(20, 10))

        # Enhanced Drag and Drop area
        self.create_drag_drop_area(main_frame)
        
        # Footer first - pack at bottom
        footer_frame = tk.Frame(main_frame, bg='#1a1a1a')
        footer_frame.pack(side='bottom', fill='x', pady=(5, 10))
        
        # Tip label
        footer_label = tk.Label(footer_frame,
                               text="💡 Tip: Customize file organization rules in Settings",
                               font=('Segoe UI', 9),
                               fg='#666666',
                               bg='#1a1a1a')
        footer_label.pack(anchor='center')

        # Separator line for visual distinction
        separator = tk.Frame(footer_frame, height=1, bg='#333333')
        separator.pack(fill='x', pady=(5, 3))

        # Credit label
        credit_label = tk.Label(footer_frame,
                               text="Made by Kahilu Chipango",
                               font=('Segoe UI', 11, 'bold'),
                               fg='#4a9eff',
                               bg='#1a1a1a')
        credit_label.pack(anchor='center')
        
        # Header section
        header_frame = tk.Frame(main_frame, bg='#1a1a1a')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, 
                              text="📁 Folder Organizer",
                              font=('Segoe UI', 24, 'bold'),
                              fg='#ffffff',
                              bg='#1a1a1a')
        title_label.pack(anchor='center')
        
        subtitle_label = tk.Label(header_frame,
                                 text="Organize your files automatically by type and extension",
                                 font=('Segoe UI', 11),
                                 fg='#a0a0a0',
                                 bg='#1a1a1a')
        subtitle_label.pack(anchor='center', pady=(3, 0))
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat', bd=1)
        content_frame.pack(fill='both', expand=True, pady=(0, 10))
        content_frame.configure(highlightbackground='#404040', highlightthickness=1, height=350)
        
        # Selected folder display
        folder_frame = tk.Frame(content_frame, bg='#2d2d2d')
        folder_frame.pack(fill='x', padx=30, pady=(20, 15))
        
        tk.Label(folder_frame,
                text="Selected Folder:",
                font=('Segoe UI', 11, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(anchor='w')
        
        self.folder_var = tk.StringVar(value="No folder selected")
        self.folder_label = tk.Label(folder_frame,
                                    textvariable=self.folder_var,
                                    font=('Segoe UI', 10),
                                    fg='#4a9eff',
                                    bg='#2d2d2d',
                                    wraplength=550,
                                    justify='left')
        self.folder_label.pack(anchor='w', pady=(5, 0))
        
        # Button container (two rows)
        button_frame = tk.Frame(content_frame, bg='#2d2d2d')
        button_frame.pack(pady=(15, 20))

        # First row
        button_row1 = tk.Frame(button_frame, bg='#2d2d2d')
        button_row1.pack()

        self.select_btn = ttk.Button(button_row1,
                                    text="🗂️  Select Folder",
                                    style='Modern.TButton',
                                    command=self.select_folder)
        self.select_btn.pack(side='left', padx=(0, 10))

        self.preview_btn = ttk.Button(button_row1,
                                     text="👁️  Preview",
                                     style='Modern.TButton',
                                     command=self.show_preview,
                                     state='disabled')
        self.preview_btn.pack(side='left', padx=(0, 10))

        self.organize_btn = ttk.Button(button_row1,
                                      text="✨  Organize",
                                      style='Modern.TButton',
                                      command=self.organize_files,
                                      state='disabled')
        self.organize_btn.pack(side='left')

        # Second row
        button_row2 = tk.Frame(button_frame, bg='#2d2d2d')
        button_row2.pack(pady=(15, 0))

        self.undo_btn = ttk.Button(button_row2,
                                   text="↩️  Undo Last",
                                   style='Secondary.TButton',
                                   command=self.undo_last_operation,
                                   state='disabled')
        self.undo_btn.pack(side='left', padx=(0, 10))

        self.settings_btn = ttk.Button(button_row2,
                                      text="⚙️  Settings",
                                      style='Secondary.TButton',
                                      command=self.open_settings)
        self.settings_btn.pack(side='left', padx=(0, 10))

        self.stats_btn = ttk.Button(button_row2,
                                   text="📊  Statistics",
                                   style='Secondary.TButton',
                                   command=self.show_statistics)
        self.stats_btn.pack(side='left')
        
        # Progress section
        progress_frame = tk.Frame(content_frame, bg='#2d2d2d')
        progress_frame.pack(fill='x', padx=30, pady=(20, 20))
        
        self.progress_var = tk.StringVar(value="Ready to organize files")
        self.progress_label = tk.Label(progress_frame,
                                      textvariable=self.progress_var,
                                      font=('Segoe UI', 10),
                                      fg='#a0a0a0',
                                      bg='#2d2d2d')
        self.progress_label.pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           mode='indeterminate',
                                           style='TProgressbar',
                                           length=590)
        self.progress_bar.pack(fill='x', pady=(10, 0))
        
        # Initialize variables
        self.selected_folder = None
        
    def create_drag_drop_area(self, parent):
        """Create an enhanced drag and drop area"""
        if DND_AVAILABLE:
            # Main drag and drop container
            self.dnd_container = tk.Frame(parent, bg='#1a1a1a')
            self.dnd_container.pack(fill='x', pady=(0, 15))
            
            # Drag and drop frame with enhanced styling
            self.dnd_frame = tk.Frame(self.dnd_container, 
                                     bg='#23272e', 
                                     height=80, 
                                     bd=2, 
                                     relief='ridge',
                                     highlightbackground='#4a9eff',
                                     highlightthickness=2)
            self.dnd_frame.pack(fill='x', padx=10)
            self.dnd_frame.pack_propagate(False)  # Maintain fixed height
            
            # Inner content frame
            inner_frame = tk.Frame(self.dnd_frame, bg='#23272e')
            inner_frame.pack(expand=True, fill='both')
            
            # Main drag text
            self.dnd_main_label = tk.Label(inner_frame, 
                                          text="📁 Drag & Drop Folder Here", 
                                          font=('Segoe UI', 14, 'bold'), 
                                          fg='#4a9eff', 
                                          bg='#23272e')
            self.dnd_main_label.pack(expand=True)
            
            # Subtitle
            self.dnd_sub_label = tk.Label(inner_frame,
                                         text="Or use the 'Select Folder' button below",
                                         font=('Segoe UI', 10),
                                         fg='#888888',
                                         bg='#23272e')
            self.dnd_sub_label.pack()
            
            # Register drop events for multiple components
            self.dnd_frame.drop_target_register(DND_FILES)
            self.dnd_frame.dnd_bind('<<Drop>>', self.on_drop_folder)
            self.dnd_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.dnd_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
            # Also register for inner components
            inner_frame.drop_target_register(DND_FILES)
            inner_frame.dnd_bind('<<Drop>>', self.on_drop_folder)
            inner_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            inner_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
            self.dnd_main_label.drop_target_register(DND_FILES)
            self.dnd_main_label.dnd_bind('<<Drop>>', self.on_drop_folder)
            self.dnd_main_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.dnd_main_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
        else:
            # Fallback message when drag and drop is not available
            fallback_frame = tk.Frame(parent, bg='#2d2d2d', height=60, bd=1, relief='ridge')
            fallback_frame.pack(fill='x', padx=10, pady=(0, 15))
            fallback_label = tk.Label(fallback_frame, 
                                     text="⚠️  Drag & Drop not available. Please use 'Select Folder' button.", 
                                     font=('Segoe UI', 11), 
                                     fg='#ffa500', 
                                     bg='#2d2d2d')
            fallback_label.pack(expand=True)
            
    def on_drag_enter(self, event):
        """Handle drag enter event - change appearance"""
        if DND_AVAILABLE and hasattr(self, 'dnd_frame'):
            self.dnd_frame.configure(bg='#2d4a3e', highlightbackground='#5cb85c')
            self.dnd_main_label.configure(text="📂 Drop Folder Here!", fg='#5cb85c', bg='#2d4a3e')
            self.dnd_sub_label.configure(fg='#aaaaaa', bg='#2d4a3e')
            
    def on_drag_leave(self, event):
        """Handle drag leave event - restore appearance"""
        if DND_AVAILABLE and hasattr(self, 'dnd_frame'):
            self.dnd_frame.configure(bg='#23272e', highlightbackground='#4a9eff')
            self.dnd_main_label.configure(text="📁 Drag & Drop Folder Here", fg='#4a9eff', bg='#23272e')
            self.dnd_sub_label.configure(fg='#888888', bg='#23272e')
            
    def on_drop_folder(self, event):
        """Enhanced drop handler with better error handling and feedback"""
        try:
            # Handle the dropped data
            dropped = event.data.strip()
            
            # Handle multiple files/folders (take the first folder)
            if '\n' in dropped or ' ' in dropped and '{' in dropped:
                # Parse multiple items or spaces in paths
                items = []
                if dropped.startswith('{'):
                    # Windows style with braces
                    import re
                    items = re.findall(r'{([^}]+)}', dropped)
                else:
                    # Split by newlines or spaces
                    items = dropped.replace('\n', ' ').split()
                
                # Find the first directory
                for item in items:
                    item = item.strip('{}')
                    if os.path.isdir(item):
                        dropped = item
                        break
            else:
                # Single item, remove braces if present
                dropped = dropped.strip('{}')
            
            # Validate that it's a directory
            if not os.path.exists(dropped):
                self.show_drop_error("Path does not exist!")
                return
                
            if not os.path.isdir(dropped):
                self.show_drop_error("Please drop a folder, not a file!")
                return
            
            # Check if folder is accessible
            try:
                os.listdir(dropped)
            except PermissionError:
                self.show_drop_error("Cannot access this folder! Permission denied.")
                return
            except Exception as e:
                self.show_drop_error(f"Cannot access folder: {str(e)}")
                return
            
            # Success - set the folder
            self.selected_folder = dropped
            display_path = dropped
            if len(display_path) > 70:
                display_path = "..." + display_path[-67:]
            self.folder_var.set(display_path)
            self.organize_btn.configure(state='normal')
            self.preview_btn.configure(state='normal')
            self.progress_var.set("Folder selected via Drag & Drop - Ready to organize!")
            
            # Visual feedback for successful drop
            if DND_AVAILABLE and hasattr(self, 'dnd_frame'):
                # Briefly show success state
                self.dnd_frame.configure(bg='#2d4a2d', highlightbackground='#28a745')
                self.dnd_main_label.configure(text="✅ Folder Selected!", fg='#28a745', bg='#2d4a2d')
                self.dnd_sub_label.configure(text=f"Ready to organize: {os.path.basename(dropped)}", fg='#aaaaaa', bg='#2d4a2d')
                
                # Reset to normal after 2 seconds
                self.root.after(2000, self.reset_drag_area)
            
        except Exception as e:
            self.show_drop_error(f"Error processing drop: {str(e)}")
            
    def show_drop_error(self, message):
        """Show error feedback in drag area and messagebox"""
        if DND_AVAILABLE and hasattr(self, 'dnd_frame'):
            self.dnd_frame.configure(bg='#4a2d2d', highlightbackground='#dc3545')
            self.dnd_main_label.configure(text="❌ Error!", fg='#dc3545', bg='#4a2d2d')
            self.dnd_sub_label.configure(text=message, fg='#aaaaaa', bg='#4a2d2d')
            
            # Reset after 3 seconds
            self.root.after(3000, self.reset_drag_area)
        
        messagebox.showwarning("Invalid Drop", message)
        
    def reset_drag_area(self):
        """Reset drag area to normal appearance"""
        if DND_AVAILABLE and hasattr(self, 'dnd_frame'):
            self.dnd_frame.configure(bg='#23272e', highlightbackground='#4a9eff')
            self.dnd_main_label.configure(text="📁 Drag & Drop Folder Here", fg='#4a9eff', bg='#23272e')
            self.dnd_sub_label.configure(text="Or use the 'Select Folder' button below", fg='#888888', bg='#23272e')
        
    def select_folder(self):
        folder_selected = filedialog.askdirectory(
            title="Select Folder to Organize",
            parent=self.root
        )
        if folder_selected:
            self.selected_folder = folder_selected
            display_path = folder_selected
            if len(display_path) > 70:
                display_path = "..." + display_path[-67:]
            self.folder_var.set(display_path)
            self.organize_btn.configure(state='normal')
            self.preview_btn.configure(state='normal')
            self.progress_var.set("Folder selected - Ready to organize!")
            
    def organize_files(self):
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
            
        # Start organizing in a separate thread to prevent GUI freezing
        self.organize_btn.configure(state='disabled')
        self.select_btn.configure(state='disabled')
        self.progress_bar.start(10)
        self.progress_var.set("Organizing files...")
        
        threading.Thread(target=self._organize_files_thread, daemon=True).start()
        
    def _organize_files_thread(self):
        try:
            app_dir = get_app_dir()
            ext_map_path = os.path.join(app_dir, "extension_map.txt")
            ext_map = load_extension_map(ext_map_path)

            if not os.path.exists(self.selected_folder):
                self.root.after(0, lambda: messagebox.showerror("Error", f"Folder not found: {self.selected_folder}"))
                return

            files_moved = 0
            files_skipped = 0
            files_renamed = 0
            total_size = 0
            operation_log = {
                "timestamp": datetime.now().isoformat(),
                "source_folder": self.selected_folder,
                "master_folder": self.settings["master_folder_name"],
                "files": []
            }

            # Process files
            files_to_process = []
            if self.settings["recursive"]:
                for root, dirs, files in os.walk(self.selected_folder):
                    # Skip master folder itself
                    if self.settings["master_folder_name"] in root:
                        continue
                    for file in files:
                        files_to_process.append(os.path.join(root, file))
            else:
                for filename in os.listdir(self.selected_folder):
                    file_path = os.path.join(self.selected_folder, filename)
                    if os.path.isfile(file_path):
                        files_to_process.append(file_path)

            for file_path in files_to_process:
                filename = os.path.basename(file_path)

                # Check exclude patterns
                if any(pattern in filename for pattern in self.settings["exclude_patterns"]):
                    files_skipped += 1
                    continue

                _, extension = os.path.splitext(filename)
                extension = extension[1:].upper()

                if not extension:
                    files_skipped += 1
                    continue

                # Check date/size rules
                skip_file = False
                for rule in self.settings.get("rules", []):
                    if rule["type"] == "date":
                        file_age_days = (time.time() - os.path.getmtime(file_path)) / 86400
                        if rule["condition"] == "older_than" and file_age_days < rule["value"]:
                            skip_file = True
                        elif rule["condition"] == "newer_than" and file_age_days > rule["value"]:
                            skip_file = True
                    elif rule["type"] == "size":
                        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                        if rule["condition"] == "larger_than" and file_size_mb < rule["value"]:
                            skip_file = True
                        elif rule["condition"] == "smaller_than" and file_size_mb > rule["value"]:
                            skip_file = True

                if skip_file:
                    files_skipped += 1
                    continue

                # Create the master folder inside the selected folder
                master_folder = os.path.join(self.selected_folder, self.settings["master_folder_name"])
                if not os.path.exists(master_folder):
                    os.makedirs(master_folder)

                folder_name = ext_map.get(extension, f"Other_{extension}")
                dest_folder = os.path.join(master_folder, folder_name)

                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)

                # Handle duplicates
                dest_filename = filename
                if os.path.exists(os.path.join(dest_folder, filename)):
                    if self.settings["handle_duplicates"] == "rename":
                        dest_filename = get_unique_filename(dest_folder, filename)
                        files_renamed += 1
                    elif self.settings["handle_duplicates"] == "skip":
                        files_skipped += 1
                        continue
                    # overwrite: just use original filename

                try:
                    file_size = os.path.getsize(file_path)
                    dest_path = os.path.join(dest_folder, dest_filename)
                    shutil.move(file_path, dest_path)

                    # Log the move for undo
                    operation_log["files"].append({
                        "original_path": file_path,
                        "new_path": dest_path,
                        "size": file_size
                    })

                    files_moved += 1
                    total_size += file_size
                except Exception as e:
                    files_skipped += 1
                    print(f"Error moving {filename}: {e}")

            # Save operation log for undo
            if files_moved > 0:
                log_path = os.path.join(app_dir, "operation_log.json")
                save_operation_log(log_path, operation_log)
                self.last_operation = operation_log

            # Update UI on main thread
            stats = {
                "files_moved": files_moved,
                "files_skipped": files_skipped,
                "files_renamed": files_renamed,
                "total_size": total_size
            }
            self.root.after(0, lambda: self._organization_complete(stats))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self._reset_ui)
            
    def _organization_complete(self, stats):
        self.progress_bar.stop()
        self.organize_btn.configure(state='normal')
        self.select_btn.configure(state='normal')

        # Enable undo if files were moved
        if stats["files_moved"] > 0:
            self.undo_btn.configure(state='normal')

        size_mb = stats["total_size"] / (1024 * 1024)
        success_msg = f"✅ Organization Complete!\n\n"
        success_msg += f"📁 Files moved: {stats['files_moved']}\n"
        if stats["files_renamed"] > 0:
            success_msg += f"✏️ Files renamed (duplicates): {stats['files_renamed']}\n"
        success_msg += f"⏭️ Files skipped: {stats['files_skipped']}\n"
        success_msg += f"💾 Total size: {size_mb:.2f} MB\n"
        success_msg += f"📅 Completed at: {datetime.now().strftime('%H:%M:%S')}"

        messagebox.showinfo("Success", success_msg)
        self.progress_var.set(f"Complete! {stats['files_moved']} files organized ({size_mb:.1f} MB)")
        
    def _reset_ui(self):
        self.progress_bar.stop()
        self.organize_btn.configure(state='normal')
        self.select_btn.configure(state='normal')
        self.progress_var.set("An error occurred - Please try again")

    def show_preview(self):
        """Show preview of what will happen during organization"""
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return

        preview_window = tk.Toplevel(self.root)
        preview_window.title("👁️ Organization Preview")
        preview_window.geometry("700x600")
        preview_window.configure(bg='#1a1a1a')
        preview_window.transient(self.root)

        # Center window
        preview_window.update_idletasks()
        x = self.root.winfo_x() - 25
        y = self.root.winfo_y() - 50
        preview_window.geometry(f"700x600+{x}+{y}")

        main_frame = tk.Frame(preview_window, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main_frame,
                text="Preview: Planned File Organization",
                font=('Segoe UI', 16, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(0, 10))

        # Calculate preview
        app_dir = get_app_dir()
        ext_map_path = os.path.join(app_dir, "extension_map.txt")
        ext_map = load_extension_map(ext_map_path)

        preview_data = {}
        total_files = 0
        total_size = 0
        skipped_count = 0

        try:
            for filename in os.listdir(self.selected_folder):
                file_path = os.path.join(self.selected_folder, filename)
                if os.path.isdir(file_path):
                    continue

                # Check exclude patterns
                if any(pattern in filename for pattern in self.settings["exclude_patterns"]):
                    skipped_count += 1
                    continue

                _, extension = os.path.splitext(filename)
                extension = extension[1:].upper()

                if not extension:
                    skipped_count += 1
                    continue

                folder_name = ext_map.get(extension, f"Other_{extension}")
                if folder_name not in preview_data:
                    preview_data[folder_name] = {"count": 0, "size": 0, "files": []}

                file_size = os.path.getsize(file_path)
                preview_data[folder_name]["count"] += 1
                preview_data[folder_name]["size"] += file_size
                preview_data[folder_name]["files"].append(filename)
                total_files += 1
                total_size += file_size

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            preview_window.destroy()
            return

        # Summary
        summary_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='ridge', bd=1)
        summary_frame.pack(fill='x', pady=(0, 15))

        tk.Label(summary_frame,
                text=f"Total Files: {total_files}  |  Total Size: {total_size/(1024*1024):.2f} MB  |  Skipped: {skipped_count}",
                font=('Segoe UI', 11),
                fg='#4a9eff',
                bg='#1a1a1a').pack(pady=10)

        # Tree view
        tree_frame = tk.Frame(main_frame, bg='#2d2d2d')
        tree_frame.pack(fill='both', expand=True, pady=(0, 15))

        tree = ttk.Treeview(tree_frame, columns=('Count', 'Size'), show='tree headings')
        tree.heading('#0', text='Destination Folder')
        tree.heading('Count', text='Files')
        tree.heading('Size', text='Size')
        tree.column('#0', width=400)
        tree.column('Count', width=100)
        tree.column('Size', width=150)

        scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Populate tree
        for folder, data in sorted(preview_data.items()):
            size_mb = data['size'] / (1024 * 1024)
            parent = tree.insert('', 'end', text=folder, values=(data['count'], f"{size_mb:.2f} MB"))
            for file in sorted(data['files'])[:10]:  # Show first 10 files
                tree.insert(parent, 'end', text=f"  {file}", values=('', ''))
            if len(data['files']) > 10:
                tree.insert(parent, 'end', text=f"  ... and {len(data['files'])-10} more", values=('', ''))

        # Buttons
        btn_frame = tk.Frame(main_frame, bg='#2d2d2d')
        btn_frame.pack(fill='x')

        ttk.Button(btn_frame,
                  text="✨ Proceed with Organization",
                  style='Modern.TButton',
                  command=lambda: [preview_window.destroy(), self.organize_files()]).pack(side='left', padx=(0, 10))

        ttk.Button(btn_frame,
                  text="❌ Cancel",
                  style='Secondary.TButton',
                  command=preview_window.destroy).pack(side='left')

    def undo_last_operation(self):
        """Undo the last file organization operation"""
        app_dir = get_app_dir()
        log_path = os.path.join(app_dir, "operation_log.json")

        logs = load_operation_logs(log_path)
        if not logs:
            messagebox.showinfo("No Operations", "No operations to undo.")
            return

        last_log = logs[-1]

        confirm = messagebox.askyesno(
            "Confirm Undo",
            f"Undo organization from {last_log['timestamp']}?\n\n"
            f"{len(last_log['files'])} files will be moved back to their original locations."
        )

        if not confirm:
            return

        # Disable buttons
        self.undo_btn.configure(state='disabled')
        self.progress_var.set("Undoing operation...")
        self.progress_bar.start(10)

        def undo_thread():
            try:
                success_count = 0
                fail_count = 0

                for file_info in last_log['files']:
                    try:
                        if os.path.exists(file_info['new_path']):
                            # Recreate original directory if needed
                            original_dir = os.path.dirname(file_info['original_path'])
                            if not os.path.exists(original_dir):
                                os.makedirs(original_dir)

                            shutil.move(file_info['new_path'], file_info['original_path'])
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception as e:
                        print(f"Error undoing {file_info['new_path']}: {e}")
                        fail_count += 1

                # Remove from log
                logs.pop()
                with open(log_path, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2)

                # Update UI
                self.root.after(0, lambda: self._undo_complete(success_count, fail_count))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Undo failed: {str(e)}"))
                self.root.after(0, self._reset_ui)

        threading.Thread(target=undo_thread, daemon=True).start()

    def _undo_complete(self, success_count, fail_count):
        self.progress_bar.stop()
        self.progress_var.set("Undo complete!")

        # Check if more operations to undo
        app_dir = get_app_dir()
        log_path = os.path.join(app_dir, "operation_log.json")
        logs = load_operation_logs(log_path)
        if not logs:
            self.undo_btn.configure(state='disabled')

        msg = f"✅ Undo Complete!\n\n"
        msg += f"✓ Files restored: {success_count}\n"
        if fail_count > 0:
            msg += f"✗ Failed: {fail_count}"

        messagebox.showinfo("Undo Complete", msg)

    def show_statistics(self):
        """Show statistics dashboard"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistics Dashboard")
        stats_window.geometry("800x600")
        stats_window.configure(bg='#1a1a1a')
        stats_window.transient(self.root)

        # Center window
        stats_window.update_idletasks()
        x = self.root.winfo_x() - 75
        y = self.root.winfo_y() - 50
        stats_window.geometry(f"800x600+{x}+{y}")

        main_frame = tk.Frame(stats_window, bg='#2d2d2d')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(main_frame,
                text="📊 Organization Statistics",
                font=('Segoe UI', 18, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(0, 20))

        # Load operation logs
        app_dir = get_app_dir()
        log_path = os.path.join(app_dir, "operation_log.json")
        logs = load_operation_logs(log_path)

        if not logs:
            tk.Label(main_frame,
                    text="No operations recorded yet.\nOrganize some files to see statistics!",
                    font=('Segoe UI', 12),
                    fg='#a0a0a0',
                    bg='#2d2d2d').pack(expand=True)
            return

        # Calculate statistics
        total_operations = len(logs)
        total_files = sum(len(log['files']) for log in logs)
        total_size = sum(sum(f['size'] for f in log['files']) for log in logs)

        # Summary cards
        summary_frame = tk.Frame(main_frame, bg='#2d2d2d')
        summary_frame.pack(fill='x', pady=(0, 20))

        def create_stat_card(parent, title, value, col):
            card = tk.Frame(parent, bg='#1a1a1a', relief='ridge', bd=2)
            card.grid(row=0, column=col, padx=10, sticky='ew')
            parent.columnconfigure(col, weight=1)

            tk.Label(card, text=title, font=('Segoe UI', 10), fg='#a0a0a0', bg='#1a1a1a').pack(pady=(10, 5))
            tk.Label(card, text=value, font=('Segoe UI', 20, 'bold'), fg='#4a9eff', bg='#1a1a1a').pack(pady=(0, 10))

        create_stat_card(summary_frame, "Total Operations", str(total_operations), 0)
        create_stat_card(summary_frame, "Files Organized", str(total_files), 1)
        create_stat_card(summary_frame, "Total Size", f"{total_size/(1024**3):.2f} GB", 2)

        # Recent operations
        tk.Label(main_frame,
                text="Recent Operations",
                font=('Segoe UI', 14, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(anchor='w', pady=(10, 5))

        tree_frame = tk.Frame(main_frame, bg='#2d2d2d')
        tree_frame.pack(fill='both', expand=True)

        tree = ttk.Treeview(tree_frame, columns=('Date', 'Files', 'Size'), show='headings')
        tree.heading('Date', text='Date & Time')
        tree.heading('Files', text='Files Moved')
        tree.heading('Size', text='Total Size')
        tree.column('Date', width=300)
        tree.column('Files', width=150)
        tree.column('Size', width=200)

        scrollbar = tk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Populate with recent operations (last 20)
        for log in reversed(logs[-20:]):
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            file_count = len(log['files'])
            size_mb = sum(f['size'] for f in log['files']) / (1024 * 1024)
            tree.insert('', 'end', values=(timestamp, file_count, f"{size_mb:.2f} MB"))

        # Close button
        ttk.Button(main_frame,
                  text="Close",
                  style='Secondary.TButton',
                  command=stats_window.destroy).pack(pady=(15, 0))

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Advanced Settings")
        settings_window.geometry("700x550")
        settings_window.configure(bg='#1a1a1a')
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Center settings window
        settings_window.update_idletasks()
        x = self.root.winfo_x() - 25
        y = self.root.winfo_y() - 25
        settings_window.geometry(f"700x550+{x}+{y}")

        # Create notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: General Settings
        general_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(general_tab, text='  General  ')

        tk.Label(general_tab,
                text="General Settings",
                font=('Segoe UI', 16, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(20, 20))

        # Master folder name
        folder_frame = tk.Frame(general_tab, bg='#2d2d2d')
        folder_frame.pack(fill='x', padx=30, pady=(0, 15))

        tk.Label(folder_frame,
                text="Master Folder Name:",
                font=('Segoe UI', 11),
                fg='#ffffff',
                bg='#2d2d2d').pack(anchor='w')

        master_folder_var = tk.StringVar(value=self.settings["master_folder_name"])
        tk.Entry(folder_frame,
                textvariable=master_folder_var,
                font=('Segoe UI', 11),
                bg='#1a1a1a',
                fg='#ffffff',
                insertbackground='#4a9eff').pack(fill='x', pady=(5, 0))

        # Duplicate handling
        dup_frame = tk.Frame(general_tab, bg='#2d2d2d')
        dup_frame.pack(fill='x', padx=30, pady=(0, 15))

        tk.Label(dup_frame,
                text="Handle Duplicates:",
                font=('Segoe UI', 11),
                fg='#ffffff',
                bg='#2d2d2d').pack(anchor='w')

        dup_var = tk.StringVar(value=self.settings["handle_duplicates"])
        dup_combo = ttk.Combobox(dup_frame,
                                textvariable=dup_var,
                                values=['rename', 'skip', 'overwrite'],
                                state='readonly')
        dup_combo.pack(fill='x', pady=(5, 0))

        # Recursive
        recursive_var = tk.BooleanVar(value=self.settings["recursive"])
        tk.Checkbutton(general_tab,
                      text="Process subdirectories recursively",
                      variable=recursive_var,
                      font=('Segoe UI', 11),
                      fg='#ffffff',
                      bg='#2d2d2d',
                      selectcolor='#1a1a1a',
                      activebackground='#2d2d2d',
                      activeforeground='#ffffff').pack(anchor='w', padx=30, pady=(0, 10))

        # Auto-organize
        auto_var = tk.BooleanVar(value=self.settings.get("auto_organize", False))
        tk.Checkbutton(general_tab,
                      text="Auto-organize (check for new files every 30 seconds)",
                      variable=auto_var,
                      font=('Segoe UI', 11),
                      fg='#ffffff',
                      bg='#2d2d2d',
                      selectcolor='#1a1a1a',
                      activebackground='#2d2d2d',
                      activeforeground='#ffffff').pack(anchor='w', padx=30, pady=(0, 10))

        # Tab 2: Exclude Patterns
        exclude_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(exclude_tab, text='  Exclude Patterns  ')

        tk.Label(exclude_tab,
                text="Files to Exclude",
                font=('Segoe UI', 16, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(20, 10))

        tk.Label(exclude_tab,
                text="Enter patterns to exclude (one per line):",
                font=('Segoe UI', 10),
                fg='#a0a0a0',
                bg='#2d2d2d').pack(padx=30, anchor='w')

        exclude_frame = tk.Frame(exclude_tab, bg='#2d2d2d')
        exclude_frame.pack(fill='both', expand=True, padx=30, pady=10)

        exclude_text = tk.Text(exclude_frame,
                              bg='#1a1a1a',
                              fg='#ffffff',
                              font=('Segoe UI', 11),
                              insertbackground='#4a9eff',
                              height=15)

        exclude_scroll = tk.Scrollbar(exclude_frame, orient='vertical', command=exclude_text.yview)
        exclude_text.configure(yscrollcommand=exclude_scroll.set)

        exclude_text.pack(side='left', fill='both', expand=True)
        exclude_scroll.pack(side='right', fill='y')

        exclude_text.insert('1.0', '\n'.join(self.settings["exclude_patterns"]))

        # Tab 3: Extension Mappings
        mapping_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(mapping_tab, text='  Extension Mappings  ')

        tk.Label(mapping_tab,
                text="File Extension Mappings",
                font=('Segoe UI', 16, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(20, 10))

        tk.Label(mapping_tab,
                text="Format: EXTENSION=Folder/Subfolder",
                font=('Segoe UI', 10),
                fg='#a0a0a0',
                bg='#2d2d2d').pack(padx=30, anchor='w')

        mapping_frame = tk.Frame(mapping_tab, bg='#2d2d2d')
        mapping_frame.pack(fill='both', expand=True, padx=30, pady=10)

        self.settings_text = tk.Text(mapping_frame,
                                    bg='#1a1a1a',
                                    fg='#ffffff',
                                    font=('Consolas', 10),
                                    insertbackground='#4a9eff',
                                    wrap='none')

        mapping_scroll = tk.Scrollbar(mapping_frame, orient='vertical', command=self.settings_text.yview)
        self.settings_text.configure(yscrollcommand=mapping_scroll.set)

        self.settings_text.pack(side='left', fill='both', expand=True)
        mapping_scroll.pack(side='right', fill='y')

        app_dir = get_app_dir()
        ext_map_path = os.path.join(app_dir, "extension_map.txt")
        ensure_extension_map(ext_map_path)

        with open(ext_map_path, 'r', encoding='utf-8') as f:
            self.settings_text.insert('1.0', f.read())

        # Save button at bottom
        btn_frame = tk.Frame(settings_window, bg='#1a1a1a')
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))

        def save_all_settings():
            try:
                # Save general settings
                self.settings["master_folder_name"] = master_folder_var.get()
                self.settings["handle_duplicates"] = dup_var.get()
                self.settings["recursive"] = recursive_var.get()

                # Handle auto-organize toggle
                old_auto = self.settings.get("auto_organize", False)
                self.settings["auto_organize"] = auto_var.get()

                # Start or stop auto-organize based on setting
                if self.settings["auto_organize"] and not old_auto:
                    self.start_auto_organize()
                elif not self.settings["auto_organize"] and old_auto:
                    self.stop_auto_organize()

                # Save exclude patterns
                exclude_content = exclude_text.get('1.0', 'end-1c').strip()
                self.settings["exclude_patterns"] = [line.strip() for line in exclude_content.split('\n') if line.strip()]

                # Save extension map
                content = self.settings_text.get('1.0', 'end-1c')
                with open(ext_map_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Save settings to JSON
                self.save_settings()

                messagebox.showinfo("Success", "All settings saved successfully!")
                settings_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

        ttk.Button(btn_frame,
                  text="💾 Save All Settings",
                  style='Modern.TButton',
                  command=save_all_settings).pack(side='left', padx=(0, 10))

        ttk.Button(btn_frame,
                  text="❌ Cancel",
                  style='Secondary.TButton',
                  command=settings_window.destroy).pack(side='left')

    def start_auto_organize(self):
        """Start automatic file organization monitoring"""
        if not self.selected_folder or not self.settings.get("auto_organize", False):
            return

        def check_and_organize():
            try:
                if not os.path.exists(self.selected_folder):
                    return

                # Count files that would be organized
                file_count = 0
                for filename in os.listdir(self.selected_folder):
                    file_path = os.path.join(self.selected_folder, filename)
                    if os.path.isfile(file_path):
                        if not any(pattern in filename for pattern in self.settings["exclude_patterns"]):
                            _, ext = os.path.splitext(filename)
                            if ext:
                                file_count += 1

                # Only organize if there are files
                if file_count > 0:
                    current_time = time.time()
                    # Only organize if 60 seconds have passed since last check
                    if current_time - self.last_check_time > 60:
                        self.last_check_time = current_time
                        self.root.after(0, self.organize_files)

            except Exception as e:
                print(f"Auto-organize error: {e}")

            # Schedule next check (every 30 seconds)
            if self.settings.get("auto_organize", False):
                self.auto_organize_job = self.root.after(30000, check_and_organize)

        check_and_organize()

    def stop_auto_organize(self):
        """Stop automatic file organization"""
        if self.auto_organize_job:
            self.root.after_cancel(self.auto_organize_job)
            self.auto_organize_job = None

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernFolderOrganizer()
    app.run()