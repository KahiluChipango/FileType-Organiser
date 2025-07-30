# FileType Organizer

A modern Python GUI tool to organize files in any folder by their extension/type.  
You can customize extension-to-folder mappings via the built-in settings editor.

## ✨ Features

- Select any folder to organize
- Automatically sorts files into folders by extension/type
- Edit extension mappings in-app (Settings)
- Modern, user-friendly interface (Tkinter)
- Remembers and creates `extension_map.txt` if missing

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed on your system

### Installation

1. Clone or download this repository and navigate to the folder:

    ```bash
    cd c:\Users\Kahilu\Desktop\pythonProject
    ```

2. Run the app:

    ```bash
    python main.py
    ```

   Or, if you have built the `.exe` (see below), just run the `.exe` file.

## 🖥️ Usage

1. **Select a folder**  
   Click "🗂️  Select Folder" and choose the folder you want to organize.

2. **Organize**  
   Click "✨  Organize Files" to sort files by type.

3. **Edit Mappings**  
   Click "⚙️  Settings" to edit which extensions go into which folders.

## 🛠 Customizing Extension Mappings

- The file `extension_map.txt` (in the same folder as the app) controls how extensions are grouped.
- Format:  
  ```
  EXT=FolderName
  ```
  Example:
  ```
  PDF=Documents
  MP4=Videos
  ```
- Edit this file directly or use the Settings window in the app.
- If `extension_map.txt` does not exist, it will be created automatically with defaults.

## 📦 Building an EXE

1. Install [PyInstaller](https://pyinstaller.org/):

    ```
    pip install pyinstaller
    ```

2. Build the executable (with a custom name):

    ```
    pyinstaller --onefile --windowed --name "FileType Organizer" main.py
    ```

3. The `.exe` will be in the `dist` folder as `FileType Organizer.exe`.  
   Make sure to copy `extension_map.txt` to the same folder as the `.exe`.

## 📄 License

This project is licensed under the MIT License.

---

Made with ❤️ by Kahilu Chipango
