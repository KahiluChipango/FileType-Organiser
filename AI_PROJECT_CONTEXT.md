# AI Project Context: FileType Organiser Pro

## Project Overview
**FileType Organiser Pro** (also called "Folder Organizer Pro") is a **premium** desktop GUI application built with Python and Tkinter that automatically organizes files with advanced features including duplicate handling, preview mode, undo system, statistics dashboard, and auto-organization.

**Version**: 2.0.0 (Major upgrade from 1.0.1)
**Author**: Kahilu Chipango
**Platform**: Cross-platform (Windows, macOS, Linux)
**Main Language**: Python 3.8+

### What's New in v2.0:
- **Preview Mode**: See planned changes before organizing
- **Undo System**: Restore files with full operation logging
- **Statistics Dashboard**: Visual organization history with charts
- **Smart Duplicate Handling**: Auto-rename, skip, or overwrite duplicates
- **Recursive Organization**: Process subdirectories automatically
- **Exclude Patterns**: Skip system files and unwanted patterns
- **Auto-Organize**: Monitor and organize new files automatically (every 30s)
- **Custom Master Folder**: User-configurable output folder name
- **Enhanced UI**: Tabbed settings, better statistics, size tracking

---

## Core Purpose
The application solves the problem of cluttered directories by automatically sorting files into a well-structured folder hierarchy. When a user selects a directory, the app moves all files into a master folder called `Organised Files - FTO`, creating subfolders based on file types (e.g., `Documents/PDF Files`, `Images/PNG Images`, `Videos/MP4 Videos`).

---

## Architecture & Key Components

### 1. Main Application (`main.py`)
**Single-file architecture** containing all application logic (~730 lines).

#### Key Classes:
- **`ModernFolderOrganizer`** (lines 200-729): Main application class
  - Manages the GUI, user interactions, and file organization logic
  - Handles both drag-and-drop and folder selection via dialog
  - Uses threading to prevent GUI freezing during file operations

#### Key Functions:
- **`get_app_dir()`** (lines 17-21): Determines application directory
  - Returns executable directory if frozen (PyInstaller), otherwise script directory
  - Critical for locating `extension_map.txt` in both development and production

- **`ensure_extension_map(filepath)`** (lines 182-185): Creates default extension map if missing
- **`load_extension_map(filepath)`** (lines 187-198): Parses `extension_map.txt` into a dictionary
  - Format: `EXTENSION=FolderPath` (case-insensitive extensions)
  - Skips blank lines and comments (lines starting with `#`)

---

## File Organization Logic

### Core Algorithm (`_organize_files_thread`, lines 573-622):
1. **Load extension map** from `extension_map.txt`
2. **Iterate through all items** in selected folder
3. **Skip directories** (only process files)
4. **Extract file extension** (uppercase, without leading dot)
5. **Create master folder** `Organised Files - FTO` inside selected directory
6. **Determine destination folder**:
   - If extension found in map: use mapped folder path
   - If not found: create `Other_{EXTENSION}` folder
7. **Create nested folder structure** (e.g., `Documents/PDF Files`)
8. **Move file** using `shutil.move()`
9. **Track statistics**: files moved vs. skipped
10. **Display completion summary** with timestamp

### Important Behavior:
- **Master folder location**: Always created INSIDE the selected folder (line 600)
- **Nested folders**: Supports multi-level paths (e.g., `VectorGraphics/Photoshop`)
- **Collision handling**: Files with same name may cause errors (caught in try-except)
- **Non-destructive**: Skips directories and files without extensions rather than deleting

---

## GUI Architecture

### Window Structure (modern dark theme):
```
┌─────────────────────────────────────────────┐
│  📁 Drag & Drop Area (if tkinterdnd2 available) │
├─────────────────────────────────────────────┤
│  Header: "📁 Folder Organizer"              │
│  Subtitle: "Organize your files..."         │
├─────────────────────────────────────────────┤
│  Selected Folder: [path display]           │
│  Buttons:                                   │
│    🗂️ Select Folder                         │
│    ✨ Organize Files (disabled until folder) │
│    ⚙️ Settings                               │
├─────────────────────────────────────────────┤
│  Progress Bar (indeterminate during run)   │
│  Status Text (shows progress/completion)   │
├─────────────────────────────────────────────┤
│  Footer: "Made by Kahilu Chipango"         │
└─────────────────────────────────────────────┘
```

### Key GUI Features:

#### 1. **Drag-and-Drop Support** (lines 378-544)
- **Optional dependency**: `tkinterdnd2` (graceful fallback if missing)
- **Drag events**:
  - `<<DragEnter>>`: Changes border to green, updates text
  - `<<DragLeave>>`: Resets to original appearance
  - `<<Drop>>`: Validates and sets folder path
- **Validation checks**:
  - Path must exist
  - Must be directory (not file)
  - Must have read permissions
- **Visual feedback**: Success (green), error (red), with auto-reset after 2-3 seconds

#### 2. **Settings Window** (`open_settings`, lines 643-722)
- **Modal dialog** (blocks main window, stays on top)
- **Editable text area** showing `extension_map.txt` contents
- **Syntax highlighting**: None (plain text editor)
- **Save/Cancel buttons**: Writes directly to `extension_map.txt`
- **Format**: `EXTENSION=Folder/Subfolder` (one per line, supports comments with `#`)

#### 3. **Threading Model** (lines 571-622)
- **Separate thread** for file operations to prevent GUI freeze
- **Thread safety**: Uses `self.root.after(0, callback)` to update GUI from worker thread
- **Progress bar**: Indeterminate mode (animated) during processing
- **State management**: Disables buttons during operation, re-enables after completion

---

## Configuration Files

### 1. `extension_map.txt` (lines 24-180 in `main.py`, stored as `DEFAULT_EXTENSION_MAP`)
**Location**: Same directory as executable/script
**Format**: `EXTENSION=Category/Subfolder`

**Categories included** (143 extensions):
- **Documents**: PDF, DOCX, TXT, XLS, XLSX, PPT, PPTX, RTF, MD, CSV, LOG, EPUB, MOBI, CBZ, CBR, etc.
- **Images**: JPG, PNG, GIF, BMP, SVG, WEBP, TIFF, ICO, HEIC, RAW formats (CR2, NEF, ARW, DNG)
- **Videos**: MP4, MKV, AVI, MOV, WMV, FLV, WEBM, MPEG, 3GP, M4V, TS, VOB, OGV, F4V
- **Audio**: MP3, WAV, AAC, FLAC, OGG, M4A, WMA, AMR, AIFF, APE, OPUS, MIDI
- **Archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ, ISO, CAB, ARJ, LZH, ACE, JAR
- **Code**: Python, JavaScript, Java, C++, C, C#, HTML, CSS, PHP, Ruby, Go, Rust, TypeScript, Shell, Batch, Perl, Swift, Kotlin, Scala, R, Jupyter, JSON, XML, YAML, SQL, Lua
- **Applications**: EXE, MSI, APK, APPX, DMG, PKG, APP, IPA
- **Fonts**: TTF, OTF, WOFF, WOFF2, EOT, PFA, PFB
- **Presentations**: KEY, ODP
- **Spreadsheets**: NUMBERS, XLSM
- **VectorGraphics**: AI, EPS, CDR, PSD, SVG, SVGZ, PDF

**Customization**: Users can add/modify mappings via Settings window or by editing the file directly.

### 2. `version.txt` (version metadata for PyInstaller)
Contains Windows executable version info structure:
- **File Version**: 1.0.1
- **Product Name**: Folder Organizer Tool
- **Company**: Kahilu Chipango
- **Copyright**: © 2025 Kahilu Chipango

### 3. `requirements.txt`
```
tkinter      # Standard library (usually included with Python)
tkinterdnd2  # Drag-and-drop support (optional)
```

### 4. PyInstaller Spec Files
- **`main.spec`**: Original build configuration
- **`FolderOrganizer.spec`**: Named build configuration
- **`FolderOrganizer_v1.0.1.spec`**: Versioned build configuration

---

## Build System

### PyInstaller Configuration:
- **Build type**: `--onefile` (single executable)
- **Window mode**: `--windowed` (no console window)
- **Output names**:
  - `FolderOrganizer.exe`
  - `FolderOrganizer_v1.0.1.exe`
  - `FileTyper Ogerniser.exe` (note typo in dist/)

### Build Output Directories:
- **`build/`**: Temporary build artifacts (analysis, TOC files, PYZ archives)
- **`dist/`**: Final executables and ZIP distributions

---

## Dependencies

### Standard Library:
- **`os`**: Path operations, directory listing
- **`shutil`**: File moving operations
- **`sys`**: Executable detection, path handling
- **`threading`**: Non-blocking file operations
- **`datetime`**: Completion timestamps

### Tkinter (Standard GUI):
- **`tkinter.Tk`**: Main window
- **`tkinter.filedialog`**: Folder selection dialog
- **`tkinter.messagebox`**: Success/error dialogs
- **`tkinter.ttk`**: Themed widgets (buttons, progress bar, styles)

### Optional Third-Party:
- **`tkinterdnd2`**: Drag-and-drop file/folder support
  - Imported with try-except (lines 10-14)
  - Sets `DND_AVAILABLE` flag to enable/disable drag-drop UI
  - Falls back gracefully to `tk.Tk` if unavailable

---

## User Workflow

### Method 1: Dialog Selection
1. Launch application
2. Click "🗂️ Select Folder"
3. Choose folder in file dialog
4. Click "✨ Organize Files"
5. View completion summary (files moved/skipped)

### Method 2: Drag-and-Drop
1. Launch application
2. Drag folder from file manager
3. Drop anywhere in drag-drop area
4. Visual feedback confirms selection
5. Click "✨ Organize Files"
6. View completion summary

### Method 3: Customize Extensions
1. Click "⚙️ Settings"
2. Edit extension mappings in text editor
3. Format: `EXT=Folder/Subfolder`
4. Click "💾 Save Changes"
5. Organize files with new mappings

---

## Error Handling

### Drag-and-Drop Validation:
- **Path doesn't exist**: Show error, reset drag area
- **Not a directory**: "Please drop a folder, not a file!"
- **Permission denied**: "Cannot access this folder!"
- **Multiple items dropped**: Finds first directory in list
- **Parse errors**: Handles Windows brace-wrapped paths `{C:\Path}`

### File Organization Errors:
- **Folder not found**: Shows error dialog, resets UI
- **File move errors**: Caught per-file, increments `files_skipped` counter
- **Exception handling**: Try-except around entire operation with error dialog

### Settings Save Errors:
- **Write failure**: Shows error dialog with exception message
- **Invalid format**: No validation (user responsible for correct syntax)

---

## Visual Design

### Color Scheme (Dark Theme):
- **Background**: `#1a1a1a` (main), `#2d2d2d` (content areas)
- **Accent**: `#4a9eff` (primary blue)
- **Text**: `#ffffff` (primary), `#a0a0a0` (secondary), `#666666` (tertiary)
- **Success**: `#28a745` (green), `#5cb85c` (light green)
- **Error**: `#dc3545` (red)
- **Hover/Active**: Darker shades of accent colors

### Typography:
- **Primary font**: Segoe UI (Windows-style modern font)
- **Code editor**: Consolas (monospace for extension map)
- **Sizes**: 24px (title), 16px (section headers), 11px (body), 10px (hints)

### Layout:
- **Window size**: 650×500px (fixed, non-resizable)
- **Centered on screen** at launch
- **Padding**: 20px main margins, 30px content padding
- **Spacing**: Consistent 10-15px between elements

---

## Git Repository

### Recent Commits (from gitStatus):
- **273ceea**: "Added a Master Folder Where all Files will be moved to"
- **bcd2f57**: "Updated the Ream me File"
- **e542e07**: "Updated version.txt"
- **3624511**: "Added a Drag and Drop Feature"
- **5f39816**: "Builds"

### Current Branch: `main`
### Modified Files (uncommitted):
- `.idea/misc.xml`
- `.idea/pythonProject.iml`

---

## Key Implementation Details for AI Assistants

### 1. File Processing Loop (lines 586-615):
```python
for filename in os.listdir(self.selected_folder):
    file_path = os.path.join(self.selected_folder, filename)

    # Skip directories
    if os.path.isdir(file_path):
        files_skipped += 1
        continue

    # Extract extension (uppercase, no dot)
    _, extension = os.path.splitext(filename)
    extension = extension[1:].upper()

    # Skip files without extension
    if not extension:
        files_skipped += 1
        continue

    # Create master folder inside selected folder
    master_folder = os.path.join(self.selected_folder, "Organised Files - FTO")

    # Get destination from map or create "Other_EXT" folder
    folder_name = ext_map.get(extension, f"Other_{extension}")
    dest_folder = os.path.join(master_folder, folder_name)

    # Create nested folders if needed
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Move file
    shutil.move(file_path, os.path.join(dest_folder, filename))
```

### 2. Extension Map Parsing (lines 187-198):
- **Case-insensitive**: Extensions converted to uppercase
- **Flexible format**: Strips whitespace around `=` delimiter
- **Comments**: Lines starting with `#` are ignored
- **Blank lines**: Skipped automatically
- **No validation**: Invalid lines with missing `=` are skipped silently

### 3. Drag-and-Drop Path Parsing (lines 462-484):
- **Multiple items**: Splits by newline or space, finds first directory
- **Windows format**: Handles `{C:\Path\To\Folder}` brace-wrapped paths
- **Unix format**: Standard space-separated paths
- **Validation**: Checks `os.path.exists()` and `os.path.isdir()` before accepting

### 4. Threading Synchronization (lines 617-622):
```python
# Update GUI from worker thread using after()
self.root.after(0, lambda: self._organization_complete(files_moved, files_skipped))
self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
self.root.after(0, self._reset_ui)
```

---

## Common User Issues & Solutions

### Issue 1: "Drag & Drop not available"
**Cause**: `tkinterdnd2` not installed
**Solution**: `pip install tkinterdnd2` or use "Select Folder" button

### Issue 2: Files not organizing
**Cause**:
- No files with recognized extensions
- Files already in subdirectories (skipped)
- Permission errors

**Solution**: Check extension map, ensure files are in root of selected folder

### Issue 3: "Other_XXX" folders appearing
**Cause**: File extension not in `extension_map.txt`
**Solution**: Add extension to map via Settings window

### Issue 4: Duplicate files
**Cause**: File with same name already exists in destination
**Solution**: `shutil.move()` may raise exception (counted as skipped)

---

## Extension Guidelines for AI Assistants

### Adding New Features:
1. **Preserve threading model**: Long operations must run in separate thread
2. **Update GUI via `after()`**: Never modify Tkinter widgets from worker thread
3. **Maintain dark theme**: Use existing color scheme constants
4. **Follow naming**: Use emoji + descriptive text for buttons
5. **Add to extension map**: Update `DEFAULT_EXTENSION_MAP` for new file types

### Modifying Extension Map:
- **Format**: `EXTENSION=Category/Subfolder`
- **Naming**: Use descriptive folder names (e.g., `Documents/PDF Files` not `docs/pdf`)
- **Categories**: Group similar file types under same category
- **Avoid duplicates**: Multiple extensions can map to same folder (e.g., JPG/JPEG)

### UI Modifications:
- **Keep window size**: 650×500px (tested for all content)
- **Use ttk widgets**: Styled buttons/progress bars (not raw Tk widgets)
- **Maintain accessibility**: Clear labels, good contrast, readable fonts
- **Test drag-drop fallback**: Ensure app works without `tkinterdnd2`

---

## Testing Checklist

### Basic Functionality:
- [ ] Select folder via dialog
- [ ] Select folder via drag-drop
- [ ] Organize files (various extensions)
- [ ] View completion summary
- [ ] Open settings window
- [ ] Edit extension map
- [ ] Save settings

### Edge Cases:
- [ ] Empty folder (0 files)
- [ ] Folder with only directories (0 files moved)
- [ ] Folder with no recognized extensions (all "Other_XXX")
- [ ] Folder with special characters in path
- [ ] Folder with very long path (>70 chars)
- [ ] Drag-drop multiple items (takes first folder)
- [ ] Drag-drop file instead of folder (error)
- [ ] Permission denied folder (error)

### Error Recovery:
- [ ] Missing `extension_map.txt` (auto-created)
- [ ] Corrupted extension map (skips bad lines)
- [ ] File move fails (increments skipped counter)
- [ ] Exception during organization (shows error, resets UI)

---

## Future Enhancement Ideas

### Suggested Improvements:
1. **Undo functionality**: Move files back to original locations
2. **Preview mode**: Show what will happen without moving files
3. **Exclude patterns**: Skip certain files/folders (e.g., `.git`, `node_modules`)
4. **Recursive organization**: Process subdirectories
5. **Custom master folder name**: Let user choose instead of "Organised Files - FTO"
6. **Duplicate handling**: Rename, skip, or overwrite options
7. **Logging**: Save organization history to file
8. **Multi-language**: Localization support
9. **Themes**: Light/dark mode toggle
10. **File filtering**: Only organize specific extensions

---

## Building & Distribution

### Development:
```bash
python main.py
```

### Building Executable:
```bash
# Basic build
pyinstaller --onefile --windowed main.py

# Versioned build with custom name
pyinstaller --onefile --windowed --name "FolderOrganizer_v1.0.1" --version-file version.txt main.py
```

### Distribution Package:
1. Copy executable from `dist/`
2. Include `extension_map.txt` in same folder
3. Include `README.md` for user instructions
4. (Optional) Create ZIP archive for easy download

---

## Project Structure Summary

```
FileType-Organiser/
├── main.py                      # Main application (single file, 730 lines)
├── extension_map.txt            # File extension mappings (143 extensions)
├── version.txt                  # PyInstaller version metadata
├── requirements.txt             # Python dependencies
├── README.md                    # User documentation
├── .gitignore                   # Git ignore rules
├── PrintDirectoryList           # Utility script (purpose unclear)
│
├── build/                       # PyInstaller build artifacts
│   ├── FolderOrganizer/
│   ├── FolderOrganizer_v1.0.1/
│   └── main/
│
├── dist/                        # Built executables
│   ├── FolderOrganizer.exe
│   ├── FolderOrganizer_v1.0.1.exe
│   ├── FolderOrganizer_v1.0.1.zip
│   ├── FileTyper Ogerniser.exe  # Typo in name
│   └── FileTyper Ogerniser.zip
│
├── *.spec                       # PyInstaller configuration files
└── .venv/                       # Python virtual environment
```

---

## AI Assistant Guidelines

### When modifying this project:
1. **Read this document first** to understand architecture
2. **Test changes locally** before committing
3. **Update this document** if making significant changes
4. **Preserve existing functionality** unless explicitly asked to change
5. **Follow existing code style** (PEP 8, descriptive names)
6. **Maintain backward compatibility** with existing `extension_map.txt` files
7. **Document new features** in README.md and this file

### When helping users:
1. **Refer to line numbers** in `main.py` for specific code locations
2. **Explain file organization logic** using examples
3. **Show extension map format** with sample entries
4. **Guide troubleshooting** using error messages and validation checks
5. **Suggest customizations** that fit the existing architecture

---

**Last Updated**: 2025-10-01
**For**: AI assistants (Claude, GPT, etc.)
**Purpose**: Complete project context for code understanding, modification, and user support

---

## Version 2.0 Premium Features (2025-10-01)

### New Features Implementation Details

#### 1. Preview Mode (`show_preview` method, ~line 837)
- **Window**: 700×600px Toplevel with tree view
- **Functionality**: Scans folder, groups by destination, shows counts/sizes
- **UI Components**: 
  - Summary frame with total files/size/skipped
  - ttk.Treeview showing folder structure
  - Expandable items (shows first 10 files per folder)
  - "Proceed" button directly calls `organize_files()`
- **No actual file operations**: Pure read-only preview

#### 2. Undo System (`undo_last_operation`, ~line 959)
- **Log file**: `operation_log.json` in app directory
- **Format**: Array of operation objects with timestamp, source, files array
- **File tracking**: Each file stores `original_path`, `new_path`, `size`
- **Undo process**: Threaded, moves files back, recreates directories if needed
- **Multi-undo**: Can undo multiple operations in reverse order
- **UI update**: Disables "Undo Last" button when no operations remain

#### 3. Statistics Dashboard (`show_statistics`, ~line 1038)
- **Window**: 800×600px with summary cards and operation list
- **Summary cards**: Total operations, files organized, total size (GB)
- **Operation list**: ttk.Treeview with last 20 operations
- **Data source**: Reads `operation_log.json`
- **Calculations**: Aggregates file counts and sizes across all operations
- **Empty state**: Shows helpful message if no operations recorded

#### 4. Duplicate Handling (integrated in `_organize_files_thread`)
- **Three modes**:
  - `rename`: Calls `get_unique_filename()` to add `_1`, `_2`, etc.
  - `skip`: Increments skipped counter, continues to next file
  - `overwrite`: Uses original filename (overwrites existing)
- **Tracking**: `files_renamed` counter shown in completion summary
- **Setting location**: Settings → General → Handle Duplicates dropdown

#### 5. Recursive Organization
- **Implementation**: `os.walk()` instead of `os.listdir()`
- **Master folder skip**: Checks if path contains master folder name
- **Setting**: Boolean checkbox in Settings → General
- **Maintains structure**: Files keep relative path from root

#### 6. Exclude Patterns
- **Storage**: `settings.json` → `exclude_patterns` array
- **Default patterns**: `.DS_Store`, `Thumbs.db`, `desktop.ini`, `.git`, `.gitignore`
- **Matching**: Substring match with `pattern in filename`
- **UI**: Multi-line text editor in Settings → Exclude Patterns tab
- **Format**: One pattern per line

#### 7. Auto-Organize (`start_auto_organize`, `stop_auto_organize`)
- **Mechanism**: Tkinter `.after()` callbacks every 30 seconds
- **Check logic**: Counts files, organizes if count > 0 and 60s since last run
- **Throttling**: Minimum 60s between auto-runs to avoid constant organizing
- **State**: Enabled/disabled via Settings → General checkbox
- **Job tracking**: Stores `self.auto_organize_job` to allow cancellation

#### 8. Custom Master Folder Name
- **Setting**: `settings.json` → `master_folder_name`
- **Default**: "Organised Files - FTO"
- **Usage**: All organization operations use this setting
- **UI**: Text entry in Settings → General tab
- **Validation**: None (user responsible for valid folder name)

#### 9. Enhanced Statistics Tracking
- **File sizes**: Tracked in bytes, displayed as MB/GB
- **Completion summary**: Shows files moved, renamed, skipped, total size, timestamp
- **Operation log**: JSON with full file list, paths, sizes, timestamps
- **Real-time display**: Progress bar with size in completion message

#### 10. Date/Size Rules (Implemented but not exposed in UI)
- **Structure**: `settings.json` → `rules` array
- **Rule types**: 
  - `date`: Check file age in days
  - `size`: Check file size in MB
- **Conditions**: `older_than`, `newer_than`, `larger_than`, `smaller_than`
- **Implementation**: Lines 731-749 in `_organize_files_thread`
- **Current UI**: Not implemented (prepared for future enhancement)

### New Configuration Files

#### settings.json (Auto-created)
```json
{
  "master_folder_name": "Organised Files - FTO",
  "exclude_patterns": [".DS_Store", "Thumbs.db", "desktop.ini", ".git", ".gitignore"],
  "handle_duplicates": "rename",
  "recursive": false,
  "auto_organize": false,
  "rules": []
}
```

#### operation_log.json (Auto-created)
```json
[
  {
    "timestamp": "2025-10-01T10:30:00.123456",
    "source_folder": "/path/to/folder",
    "master_folder": "Organised Files - FTO",
    "files": [
      {
        "original_path": "/path/to/folder/file.pdf",
        "new_path": "/path/to/folder/Organised Files - FTO/Documents/PDF Files/file.pdf",
        "size": 1048576
      }
    ]
  }
]
```

### New UI Components

#### Main Window Changes (v2.0)
```
┌─────────────────────────────────────────────┐
│  📁 Drag & Drop Area                        │
├─────────────────────────────────────────────┤
│  Header: "📁 Folder Organizer"              │
├─────────────────────────────────────────────┤
│  Selected Folder: [path]                   │
│  Buttons Row 1:                             │
│    🗂️ Select Folder                         │
│    👁️ Preview (NEW)                         │
│    ✨ Organize                               │
│  Buttons Row 2:                             │
│    ↩️ Undo Last (NEW)                       │
│    ⚙️ Settings                               │
│    📊 Statistics (NEW)                      │
├─────────────────────────────────────────────┤
│  Progress Bar + Size Display (ENHANCED)    │
└─────────────────────────────────────────────┘
```

#### Settings Window (Tabbed, v2.0)
- **Tab 1 - General**: Master folder, duplicates, recursive, auto-organize
- **Tab 2 - Exclude Patterns**: Multi-line text editor
- **Tab 3 - Extension Mappings**: Original extension editor

### Key Line Numbers (Approximate, v2.0)

- **Settings loading**: Lines 255-287
- **Duplicate handler**: Lines 204-213 (`get_unique_filename`)
- **Operation logging**: Lines 215-237 (`save_operation_log`, `load_operation_logs`)
- **Preview mode**: Lines 837-957
- **Undo system**: Lines 959-1036
- **Statistics**: Lines 1038-1130
- **Enhanced settings**: Lines 1132-1322
- **Auto-organize**: Lines 1324-1365
- **Main organization**: Lines 680-808 (heavily enhanced)

### Performance Considerations

- **Threading**: All file operations run in separate threads
- **UI updates**: Use `root.after(0, callback)` for thread-safe updates
- **Auto-organize throttling**: 60s minimum between runs
- **Log file size**: Grows with each operation (consider periodic cleanup)
- **Preview performance**: Fast (read-only, no file moves)
- **Undo performance**: Same as organization (moves files back)

### Testing Checklist for v2.0

#### New Features:
- [ ] Preview shows accurate file counts and folder structure
- [ ] Undo restores all files to original locations
- [ ] Statistics dashboard displays operation history
- [ ] Duplicate rename creates `_1`, `_2`, etc. correctly
- [ ] Recursive organization processes subdirectories
- [ ] Exclude patterns skip specified files
- [ ] Auto-organize runs every 30s when enabled
- [ ] Custom master folder name is used
- [ ] Size statistics show in MB/GB correctly
- [ ] Settings persist across app restarts

#### Integration:
- [ ] All features work together (e.g., undo after recursive organize)
- [ ] Settings changes take effect immediately
- [ ] Preview matches actual organization results
- [ ] Statistics track all organization methods

---

**Version**: 2.0.0
**Major Update Date**: 2025-10-01
**Total Lines Added**: ~600+ lines (original ~730, now ~1370)
**New Methods**: 5 major methods (preview, undo, stats, auto-organize helpers)
**New Files**: `settings.json`, `operation_log.json`
