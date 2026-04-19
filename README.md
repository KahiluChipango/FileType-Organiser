# FileType Organizer Pro v2.0

A **premium** Python GUI tool to intelligently organize files in any folder with advanced features like duplicate handling, undo system, preview mode, statistics dashboard, and auto-organization.

## ✨ Features

### Core Features
- **Drag & Drop** support - Drop a folder anywhere in the window
- **Smart duplicate handling** - Auto-rename, skip, or overwrite duplicates
- **Preview mode** - See exactly what will happen before organizing
- **Undo system** - Restore files to original locations with one click
- **Statistics dashboard** - Track organization history with visual stats
- **Recursive organization** - Process subdirectories automatically

### Advanced Features
- **Custom master folder name** - Change default "Organised Files - FTO" name
- **Exclude patterns** - Skip system files (.DS_Store, .git, etc.)
- **Date/size rules** - Organize based on file age or size (coming soon)
- **Auto-organize** - Monitor folder and auto-organize new files every 30 seconds
- **Advanced statistics** - File counts, sizes, operation history

### User Experience
- Modern, dark-themed interface
- Real-time progress tracking with size statistics
- Detailed completion summaries
- Tabbed settings window for easy configuration
- 143 pre-configured file extensions across 15 categories

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed on your system

### Installation

1. Clone or download this repository and navigate to the folder:

    ```bash
    cd FileType-Organiser
    ```

2. Install requirements:

    ```bash
    pip install -r requirements.txt
    ```

   > **Note:**  
   > The app uses `tkinterdnd2` for drag-and-drop support.  
   > If you see a warning about drag & drop not being available, install it with:
   > ```
   > pip install tkinterdnd2
   > ```

3. Run the app:

    ```bash
    python main.py
    ```

   Or, if you have built the `.exe` (see below), just run the `.exe` file.

## 🖥️ Usage

### Basic Workflow
1. **Select a folder**
   - Click "🗂️ Select Folder" and choose the folder, **or**
   - **Drag & Drop** a folder into the app window

2. **Preview (Optional)**
   Click "👁️ Preview" to see planned changes before organizing

3. **Organize**
   Click "✨ Organize" to sort files by type

4. **View Statistics**
   Click "📊 Statistics" to see organization history and stats

5. **Undo if needed**
   Click "↩️ Undo Last" to restore files to original locations

### Advanced Features

#### Preview Mode
See exactly how files will be organized:
- File counts per category
- Total size calculations
- Folder structure preview
- Proceed or cancel before making changes

#### Duplicate Handling
Configure how to handle duplicate filenames:
- **Rename**: Adds `_1`, `_2`, etc. to duplicate files
- **Skip**: Leaves duplicates in original location
- **Overwrite**: Replaces existing file (use with caution!)

#### Undo System
- Automatically logs all operations
- One-click restore to original state
- Maintains operation history
- Can undo multiple operations

#### Statistics Dashboard
Track your organization activity:
- Total operations performed
- Files organized (count and size)
- Recent operation history
- Visual summary cards

#### Auto-Organize
Set it and forget it:
- Monitors selected folder every 30 seconds
- Automatically organizes new files
- Perfect for Downloads folder
- Enable in Settings → General

#### Settings Configuration
**General Tab:**
- Master folder name (custom output folder)
- Duplicate handling strategy
- Recursive organization toggle
- Auto-organize enable/disable

**Exclude Patterns Tab:**
- Add patterns to skip (one per line)
- Default excludes: .DS_Store, Thumbs.db, .git
- Supports partial filename matching

**Extension Mappings Tab:**
- Edit file extension mappings
- Format: `EXTENSION=Category/Subfolder`
- 143 extensions pre-configured

## 🛠 Customizing Extension Mappings

- The file `extension_map.txt` (in the same folder as the app) controls how extensions are grouped.
- Format:  
  ```
  EXT=FolderName/SubFolder
  ```
  Example:
  ```
  PDF=Documents/PDF Files
  MP4=Videos/MP4 Videos
  ```
- Edit this file directly or use the Settings window in the app.
- If `extension_map.txt` does not exist, it will be created automatically with defaults.

## 📦 Building an EXE

1. Install [PyInstaller](https://pyinstaller.org/):

    ```bash
    pip install pyinstaller
    ```

2. Build the executable with version info:

    ```bash
    pyinstaller --onefile --windowed --name "FolderOrganizerPro" --version-file version.txt main.py
    ```

3. The `.exe` will be in the `dist` folder as `FolderOrganizerPro.exe`.

**Note:** The app automatically creates `extension_map.txt`, `settings.json`, and `operation_log.json` in the same directory as the executable.

## 📊 New in Version 2.0

### Major Features Added:
- ✅ **Preview Mode** - See planned changes before organizing
- ✅ **Undo System** - Restore files with operation logging
- ✅ **Statistics Dashboard** - Visual organization history
- ✅ **Duplicate Handling** - Smart rename/skip/overwrite options
- ✅ **Recursive Organization** - Process subdirectories
- ✅ **Exclude Patterns** - Skip unwanted files
- ✅ **Auto-Organize** - Automatic monitoring and organization
- ✅ **Custom Master Folder** - Configurable output folder name
- ✅ **Enhanced Statistics** - File sizes, counts, and detailed summaries
- ✅ **Tabbed Settings** - Better organized configuration interface

### Technical Improvements:
- Operation logging system for undo functionality
- JSON-based settings storage
- Thread-safe file operations
- Improved error handling and user feedback
- Size tracking and display in MB/GB
- Timestamp tracking for all operations

## 📄 License

This project is licensed under the MIT License.

---

Made with ❤️ by Kahilu Chipango
