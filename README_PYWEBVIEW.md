# FileType Organizer Pro v2.0 — PyWebView Edition

A **modern, cross-platform** desktop application to intelligently organize files by type. Built with PyWebView for a native feel with web technologies.

![FileType Organizer Pro](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)

## ✨ Features

### Core Features
- 🎯 **Smart folder organization** — Automatically sorts files into categorized subfolders
- 👁️ **Preview mode** — See exactly what will happen before organizing
- ↩️ **Undo system** — Restore files to original locations with one click
- 📊 **Statistics dashboard** — Track organization history with visual stats and category breakdown
- ⚙️ **Flexible settings** — Customize behavior, duplicates handling, and exclusions

### Advanced Features
- **Custom master folder name** — Change default "Organised Files - FTO" name
- **Exclude patterns** — Skip system files (.DS_Store, .git, etc.)
- **Duplicate handling** — Auto-rename, skip, or overwrite duplicates
- **Recursive organization** — Process subdirectories automatically
- **Category visualization** — See breakdown of organized files by category
- **143 pre-configured file extensions** across 15 categories

### User Experience
- Modern, clean interface with warm color palette
- Real-time progress tracking
- Detailed completion summaries
- Native desktop integration
- Cross-platform support (macOS, Windows, Linux)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed on your system

### Installation

1. Clone or download this repository:

    ```bash
    git clone https://github.com/yourusername/FileType-Organiser.git
    cd FileType-Organiser
    ```

2. Install requirements:

    ```bash
    pip3 install -r requirements.txt
    ```

3. Run the app:

    ```bash
    python3 pywebview_main.py
    ```

## 🖥️ Usage

### Basic Workflow

1. **Select a folder**
   - Click "Drop a folder here" or browse your computer

2. **Preview (Optional)**
   - Click "Preview" to see planned changes before organizing

3. **Organize**
   - Click "Organize Now" to sort files by type

4. **View Statistics**
   - Click the "Statistics" tab to see organization history and category breakdown

5. **Undo if needed**
   - Click "Undo" to restore files to original locations

### Screens

#### Home Screen
- Drop zone for folder selection
- Real-time folder scanning with file counts
- Quick stats for Images, Documents, and Videos
- Preview and Organize buttons

#### Preview Screen
- Full breakdown of planned moves
- Files grouped by destination folder
- File counts and sizes per category
- Confirm or cancel before organizing

#### Progress Screen
- Real-time progress bar with percentage
- Current file being processed
- Visual step indicators (Scanning → Creating folders → Moving files → Finishing)

#### Complete Screen
- Summary of organization results
- Files moved, renamed, and skipped counts
- Total size organized
- Quick access to open organized folder
- Undo button if needed

#### Statistics Screen
- Total runs, files organized, and total size cards
- **Category breakdown** with visual bars showing distribution
- Operation history with timestamps and details

#### Settings Screen
Three tabs for comprehensive configuration:

**General:**
- Master folder name customization
- Recursive organization toggle
- Auto-organize enable/disable
- Duplicate handling (Rename / Skip / Overwrite)

**Exclude Patterns:**
- Add patterns to skip (one per line)
- Default excludes: `.DS_Store`, `Thumbs.db`, `.git`

**Extension Map:**
- Edit file extension mappings
- Format: `EXTENSION=Category/Subfolder`
- 143 extensions pre-configured

## 🛠 Customizing Extension Mappings

The file `extension_map.txt` controls how extensions are grouped:

```
PDF=Documents/PDF Files
MP4=Videos/MP4 Videos
JPG=Images/JPG Images
PY=Code/Python
```

Edit this file directly or use the Settings screen in the app.

## 📦 Building an Executable

See [BUILD.md](BUILD.md) for detailed instructions on building for macOS, Windows, and Linux.

Quick build:

```bash
pip3 install pyinstaller
pyinstaller FileTypeOrganizer.spec
```

The executable will be in the `dist/` folder.

## 🏗️ Architecture

### Tech Stack
- **Frontend:** HTML5, CSS3, JavaScript (vanilla)
- **Backend:** Python with PyWebView
- **Bridge:** JavaScript ↔ Python communication via `window.pywebview.api`
- **Storage:** JSON files for settings and logs

### File Structure
```
FileType-Organiser/
├── pywebview_main.py       # App launcher
├── pywebview_api.py        # Python backend API
├── app.html                # Complete UI (HTML/CSS/JS)
├── extension_map.txt       # File extension mappings
├── settings.json           # User settings (auto-created)
├── operation_log.json      # Organization history (auto-created)
├── app.log                 # Application logs (auto-created)
├── FileTypeOrganizer.spec  # PyInstaller configuration
├── BUILD.md                # Build instructions
└── README_PYWEBVIEW.md     # This file
```

## 🎨 Design Tokens

The app uses a carefully crafted design system:

```
Background:     #f8f8f5   (warm off-white)
Surface:        #ffffff   (cards, panels)
Surface 2:      #f2f2ef   (hover states, inputs)
Border:         #e4e4dc   (dividers)
Text primary:   #1a1a17
Text secondary: #5c5c56
Text tertiary:  #9b9b93
Accent:         #1a6cf0   (primary blue)
Green:          #16a34a   (success)
Amber:          #d97706   (warning)
Red:            #dc2626   (error)

Font:           'Plus Jakarta Sans'
Mono font:      'JetBrains Mono'
Border radius:  12px (standard), 10px (buttons), 99px (pills)
```

## 📊 New in Version 2.0 (PyWebView Edition)

### Major Features Added:
- ✅ **Modern web-based UI** with native desktop integration
- ✅ **Category breakdown visualization** in Statistics
- ✅ **Enhanced error handling** and logging
- ✅ **Real-time progress updates** with file-by-file tracking
- ✅ **Improved preview system** with detailed file lists
- ✅ **Cross-platform support** (macOS, Windows, Linux)

### Technical Improvements:
- PyWebView architecture for better performance
- Comprehensive logging system
- Better error handling throughout
- Thread-safe file operations
- Category-based statistics tracking
- Improved settings management

## 🔒 Privacy & Security

- **Local-only processing:** All file operations happen on your machine
- **No internet required:** App works completely offline
- **No tracking:** No analytics or data collection
- **Open source:** Review the code yourself

## 🐛 Troubleshooting

### App won't start
- Check that Python 3.8+ is installed: `python3 --version`
- Verify all dependencies are installed: `pip3 install -r requirements.txt`
- Check `app.log` for errors

### Permission errors
- Ensure you have read/write access to the target folder
- On macOS, grant Full Disk Access in System Preferences → Security & Privacy

### Files not organizing
- Check that files have recognizable extensions
- Review exclude patterns in Settings
- Check `app.log` for specific errors

## 📄 License

This project is licensed under the MIT License.

## 🙏 Credits

- **Developer:** Kahilu Chipango
- **UI Design:** Claude Design
- **Fonts:** Plus Jakarta Sans, JetBrains Mono
- **Technology:** PyWebView, Python

---

**Made with ❤️ by Kahilu Chipango**
