# FileType Organizer Pro — Build Instructions

This document explains how to build FileType Organizer Pro as a standalone executable for macOS, Windows, and Linux.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Development Setup

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Run in Development Mode

```bash
python3 pywebview_main.py
```

This will launch the app in development mode. The app window should open displaying the FileType Organizer Pro interface.

### 3. Enable Debug Mode (Optional)

To see the DevTools console for debugging, edit `pywebview_main.py` and change:

```python
webview.start(debug=True)  # Changed from False
```

## Building for Production

### Install PyInstaller

```bash
pip3 install pyinstaller
```

### macOS

Build a `.app` bundle:

```bash
pyinstaller FileTypeOrganizer.spec
```

The built app will be in `dist/FileTypeOrganizerPro.app`.

To create a DMG for distribution:

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "FileType Organizer Pro" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 425 120 \
  "FileTypeOrganizerPro.dmg" \
  "dist/FileTypeOrganizerPro.app"
```

### Windows

Build a `.exe`:

```bash
pyinstaller FileTypeOrganizer.spec
```

The executable will be in `dist/FileTypeOrganizerPro.exe`.

**Note:** On Windows, you may want to add an icon. Create or download an `.ico` file and update the spec file:

```python
exe = EXE(
    ...
    icon='app_icon.ico',  # Add this line
    ...
)
```

### Linux

Build a Linux executable:

```bash
pyinstaller FileTypeOrganizer.spec
```

The executable will be in `dist/FileTypeOrganizerPro`.

## Customization

### App Name and Version

Edit `FileTypeOrganizer.spec`:

```python
name='YourAppName',
...
'CFBundleShortVersionString': '2.0.0',  # Change version
```

### Window Size

Edit `pywebview_main.py`:

```python
window = webview.create_window(
    ...
    width=900,   # Change width
    height=620,  # Change height
    ...
)
```

### App Icon

1. Create or obtain an icon file:
   - macOS: `.icns` file
   - Windows: `.ico` file
   - Linux: `.png` file (512x512 recommended)

2. Update `FileTypeOrganizer.spec`:

```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # or .icns on macOS
    ...
)
```

## File Structure

After building, the app bundle/executable includes:

- `pywebview_main.py` — App entry point
- `pywebview_api.py` — Python backend API
- `app.html` — UI frontend
- `extension_map.txt` — File extension mappings (auto-created if missing)

The following files are created at runtime in the same directory as the executable:

- `settings.json` — User settings
- `operation_log.json` — Organization history
- `app.log` — Application log file

## Troubleshooting

### Import Errors

If you get import errors during build, add the missing module to `hiddenimports` in `FileTypeOrganizer.spec`:

```python
hiddenimports=[
    'webview',
    'bottle',
    'proxy_tools',
    'your_missing_module',  # Add here
],
```

### File Not Found

If the app can't find `app.html` at runtime, ensure it's included in `datas`:

```python
datas=[
    ('app.html', '.'),
    ('extension_map.txt', '.'),
],
```

### macOS Code Signing

For macOS distribution, you'll need to sign the app:

```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  dist/FileTypeOrganizerPro.app
```

### macOS Notarization

For distribution outside the Mac App Store:

1. Compress the app:
```bash
ditto -c -k --keepParent dist/FileTypeOrganizerPro.app FileTypeOrganizerPro.zip
```

2. Submit for notarization:
```bash
xcrun notarytool submit FileTypeOrganizerPro.zip \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait
```

3. Staple the notarization ticket:
```bash
xcrun stapler staple dist/FileTypeOrganizerPro.app
```

## Performance Tips

- Use `--onefile` for single executable (slower startup)
- Use `--onedir` for faster startup (multiple files)
- Use `upx=True` for smaller file size (current default)
- Set `console=False` for GUI apps (current default)

## Clean Build

To ensure a fresh build:

```bash
rm -rf build dist
pyinstaller --clean FileTypeOrganizer.spec
```

## Testing the Build

After building, test the executable:

1. Navigate to `dist/`
2. Run the app
3. Test all features:
   - Folder selection
   - File preview
   - Organization
   - Undo
   - Statistics
   - Settings

## Support

For issues or questions:
- Check the logs in `app.log`
- Review `operation_log.json` for operation history
- See README.md for feature documentation
