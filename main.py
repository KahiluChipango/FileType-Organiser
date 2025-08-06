import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import threading
from datetime import datetime

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

class ModernFolderOrganizer:
    def __init__(self):
        # Use TkinterDnD.Tk if available, else fallback to tk.Tk
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.setup_styles()
        
    def setup_window(self):
        self.root.title("✨ Modern Folder Organizer")
        self.root.geometry("650x500")  # Slightly larger for better drag area
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"650x500+{x}+{y}")
        
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
        content_frame.configure(highlightbackground='#404040', highlightthickness=1)
        
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
        
        # Button container
        button_frame = tk.Frame(content_frame, bg='#2d2d2d')
        button_frame.pack(pady=15)
        
        # Modern buttons
        self.select_btn = ttk.Button(button_frame,
                                    text="🗂️  Select Folder",
                                    style='Modern.TButton',
                                    command=self.select_folder)
        self.select_btn.pack(side='left', padx=(0, 15))
        
        self.organize_btn = ttk.Button(button_frame,
                                      text="✨  Organize Files",
                                      style='Modern.TButton',
                                      command=self.organize_files,
                                      state='disabled')
        self.organize_btn.pack(side='left', padx=(0, 15))
        
        self.settings_btn = ttk.Button(button_frame,
                                      text="⚙️  Settings",
                                      style='Secondary.TButton',
                                      command=self.open_settings)
        self.settings_btn.pack(side='left')
        
        # Progress section
        progress_frame = tk.Frame(content_frame, bg='#2d2d2d')
        progress_frame.pack(fill='x', padx=30, pady=(15, 20))
        
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
            
            for filename in os.listdir(self.selected_folder):
                file_path = os.path.join(self.selected_folder, filename)
                if os.path.isdir(file_path):
                    files_skipped += 1
                    continue
                    
                _, extension = os.path.splitext(filename)
                extension = extension[1:].upper()
                
                if not extension:
                    files_skipped += 1
                    continue
                    
                folder_name = ext_map.get(extension, f"Other_{extension}")
                dest_folder = os.path.join(self.selected_folder, folder_name)
                
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                    
                try:
                    shutil.move(file_path, os.path.join(dest_folder, filename))
                    files_moved += 1
                except Exception as e:
                    files_skipped += 1
                    print(f"Error moving {filename}: {e}")
            
            # Update UI on main thread
            self.root.after(0, lambda: self._organization_complete(files_moved, files_skipped))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, self._reset_ui)
            
    def _organization_complete(self, files_moved, files_skipped):
        self.progress_bar.stop()
        self.organize_btn.configure(state='normal')
        self.select_btn.configure(state='normal')
        
        success_msg = f"✅ Organization Complete!\n\n"
        success_msg += f"📁 Files moved: {files_moved}\n"
        success_msg += f"⏭️ Files skipped: {files_skipped}\n"
        success_msg += f"📅 Completed at: {datetime.now().strftime('%H:%M:%S')}"
        
        messagebox.showinfo("Success", success_msg)
        self.progress_var.set(f"Complete! {files_moved} files organized")
        
    def _reset_ui(self):
        self.progress_bar.stop()
        self.organize_btn.configure(state='normal')
        self.select_btn.configure(state='normal')
        self.progress_var.set("An error occurred - Please try again")
        
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Organizer Settings")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#1a1a1a')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center settings window
        settings_window.update_idletasks()
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        settings_window.geometry(f"500x400+{x}+{y}")
        
        # Settings content
        settings_frame = tk.Frame(settings_window, bg='#2d2d2d')
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(settings_frame,
                text="File Extension Mappings",
                font=('Segoe UI', 16, 'bold'),
                fg='#ffffff',
                bg='#2d2d2d').pack(pady=(0, 15))
        
        tk.Label(settings_frame,
                text="Edit the mappings below (format: EXTENSION=FOLDER)",
                font=('Segoe UI', 10),
                fg='#a0a0a0',
                bg='#2d2d2d').pack(pady=(0, 10))
        
        # Text editor for extension map
        text_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        text_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        self.settings_text = tk.Text(text_frame,
                                    bg='#1a1a1a',
                                    fg='#ffffff',
                                    font=('Consolas', 10),
                                    insertbackground='#4a9eff',
                                    selectbackground='#4a9eff',
                                    selectforeground='#ffffff',
                                    wrap='none')
        
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.settings_text.yview)
        self.settings_text.configure(yscrollcommand=scrollbar.set)
        
        self.settings_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load current settings
        app_dir = get_app_dir()
        ext_map_path = os.path.join(app_dir, "extension_map.txt")
        ensure_extension_map(ext_map_path)
        
        with open(ext_map_path, 'r', encoding='utf-8') as f:
            self.settings_text.insert('1.0', f.read())
        
        # Buttons
        btn_frame = tk.Frame(settings_frame, bg='#2d2d2d')
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame,
                  text="💾 Save Changes",
                  style='Modern.TButton',
                  command=lambda: self.save_settings(ext_map_path, settings_window)).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame,
                  text="❌ Cancel",
                  style='Secondary.TButton',
                  command=settings_window.destroy).pack(side='left')
        
    def save_settings(self, ext_map_path, settings_window):
        try:
            content = self.settings_text.get('1.0', 'end-1c')
            with open(ext_map_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Success", "Settings saved successfully!")
            settings_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernFolderOrganizer()
    app.run()