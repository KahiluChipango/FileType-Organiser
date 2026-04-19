# FolderOrganizerPro v2.0 - Installation Guide

## 📦 What's Included

Your build contains:
- **FolderOrganizerPro.app** - macOS Application (11MB)
- **FolderOrganizerPro** - Command-line executable (11MB)

## 🍎 macOS Installation

### Method 1: Use the .app Bundle (Recommended)

1. **Locate the app**:
   ```
   dist/FolderOrganizerPro.app
   ```

2. **Move to Applications** (optional):
   - Drag `FolderOrganizerPro.app` to your `/Applications` folder
   - Or keep it anywhere you prefer

3. **First Launch**:
   - Double-click `FolderOrganizerPro.app`
   - If macOS shows "unidentified developer" warning:
     - Right-click the app → Open
     - Click "Open" in the dialog
     - Or: System Preferences → Security & Privacy → Click "Open Anyway"

4. **Grant Permissions** (if asked):
   - Allow access to folders you want to organize
   - This is required for the app to move files

### Method 2: Command-line Executable

1. **Run from terminal**:
   ```bash
   ./dist/FolderOrganizerPro
   ```

2. **Or add to PATH**:
   ```bash
   sudo cp dist/FolderOrganizerPro /usr/local/bin/
   folderorgpro  # Run from anywhere
   ```

## 🖥️ Using the Application

### First Time Setup
1. Launch the app
2. The app will auto-create configuration files in its directory:
   - `extension_map.txt` - File type mappings (143 extensions)
   - `settings.json` - Your preferences
   - `operation_log.json` - Undo history (created after first use)

### Basic Usage
1. **Select a Folder**:
   - Click "🗂️ Select Folder" and choose a folder
   - OR drag and drop a folder into the app window

2. **Preview (Optional)**:
   - Click "👁️ Preview" to see what will happen
   - Review file counts and folder structure
   - Click "Proceed" or "Cancel"

3. **Organize**:
   - Click "✨ Organize" to sort files by type
   - Files move to `Organised Files - FTO/` folder
   - View completion summary with statistics

4. **Undo if Needed**:
   - Click "↩️ Undo Last" to restore files
   - Can undo multiple operations

5. **View Statistics**:
   - Click "📊 Statistics" to see organization history
   - View total files, operations, and sizes

6. **Configure Settings**:
   - Click "⚙️ Settings" for advanced options
   - Set duplicate handling, exclusions, auto-organize

## ⚙️ Advanced Features

### Duplicate Handling
Settings → General → Handle Duplicates:
- **Rename**: Adds `_1`, `_2` to duplicate files
- **Skip**: Leaves duplicates in place
- **Overwrite**: Replaces existing file (careful!)

### Exclude Patterns
Settings → Exclude Patterns:
- Add filenames or patterns to skip (one per line)
- Default: `.DS_Store`, `Thumbs.db`, `.git`, etc.

### Recursive Organization
Settings → General → Process subdirectories:
- Organizes files in all subfolders
- Maintains folder structure

### Auto-Organize
Settings → General → Auto-organize:
- Monitors folder every 30 seconds
- Automatically organizes new files
- Perfect for Downloads folder

### Custom Master Folder
Settings → General → Master Folder Name:
- Change from "Organised Files - FTO" to your preference
- E.g., "Organized", "Sorted Files", etc.

### Extension Mappings
Settings → Extension Mappings:
- Edit where file types are organized
- Format: `EXTENSION=Category/Subfolder`
- Example: `PDF=Documents/PDF Files`

## 📁 File Locations

**Configuration files are stored next to the app**:

If using `.app`:
```
/Applications/FolderOrganizerPro.app/Contents/MacOS/
├── extension_map.txt
├── settings.json
└── operation_log.json
```

To access: Right-click app → Show Package Contents → Contents → MacOS

## 🔧 Troubleshooting

### "App can't be opened because it's from an unidentified developer"
**Solution**: Right-click app → Open → Click "Open" button

### "App doesn't have permission to access files"
**Solution**: System Preferences → Security & Privacy → Privacy → Files and Folders → Enable access

### Settings not saving
**Solution**: Make sure the app has write permissions in its directory

### Undo not working
**Solution**: Check if `operation_log.json` exists. Undo only works after organizing at least once.

### Drag & Drop not working
**Solution**: If tkinterdnd2 wasn't available during build, use "Select Folder" button instead

## 🆘 Need Help?

### Check logs
The app prints errors to console:
```bash
# Run from terminal to see error messages
./dist/FolderOrganizerPro.app/Contents/MacOS/FolderOrganizerPro
```

### Reset settings
Delete configuration files to restore defaults:
```bash
cd /Applications/FolderOrganizerPro.app/Contents/MacOS/
rm settings.json extension_map.txt operation_log.json
```

### GitHub Issues
Report bugs at: https://github.com/yourusername/FileType-Organiser/issues

## 🎉 Quick Start Checklist

- [ ] Copy `FolderOrganizerPro.app` to Applications
- [ ] Double-click to launch (right-click → Open if needed)
- [ ] Grant folder access permissions
- [ ] Select a test folder with a few files
- [ ] Click "Preview" to see what will happen
- [ ] Click "Organize" to try it out
- [ ] Click "Statistics" to view results
- [ ] Configure Settings as needed

## 📊 What Gets Organized?

**143 file extensions across 15 categories**:
- Documents (PDF, DOCX, TXT, XLS, PPT, etc.)
- Images (JPG, PNG, GIF, SVG, RAW formats)
- Videos (MP4, MKV, AVI, MOV, etc.)
- Audio (MP3, WAV, FLAC, etc.)
- Archives (ZIP, RAR, 7Z, etc.)
- Code (Python, JS, Java, C++, etc.)
- Applications (EXE, DMG, APK, etc.)
- Fonts (TTF, OTF, WOFF, etc.)
- And more!

## 🚀 Pro Tips

1. **Test first**: Use Preview mode on a test folder before organizing important files
2. **Backup important data**: Although undo exists, always have backups
3. **Customize exclusions**: Add `.tmp`, `.cache`, etc. to exclude patterns
4. **Use auto-organize**: Great for keeping Downloads folder clean
5. **Check statistics**: Track how much you've organized over time

---

**Version**: 2.0.0
**Built**: October 2025
**Platform**: macOS (Tested on macOS 13.6.1)
**Made by**: Kahilu Chipango
**License**: MIT
