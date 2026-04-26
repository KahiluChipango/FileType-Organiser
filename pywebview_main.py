"""
FileType Organizer Pro — PyWebView Entry Point
===============================================
Install:
    pip install pywebview

Run:
    python pywebview_main.py

Build to .exe / .app:
    pip install pyinstaller
    pyinstaller --onefile --windowed --name "FileTypeOrganizer" pywebview_main.py
"""

import webview
from pywebview_api import Api

def main():
    api = Api()

    window = webview.create_window(
        title       = "FileType Organizer Pro",
        url         = "app.html",          # your HTML UI
        js_api      = api,                 # expose Api() to window.pywebview.api
        width       = 900,
        height      = 620,
        min_size    = (760, 540),
        resizable   = True,
        text_select = False,
        confirm_close = False,
    )

    # Give the api a reference to the window so it can push events
    api._window = window

    # Start — debug=True shows DevTools in development
    webview.start(debug=False)

if __name__ == "__main__":
    main()
