# Handoff: FileType Organizer Pro — Desktop App

## Overview
FileType Organizer Pro is a cross-platform desktop application that automatically sorts files in a folder into categorised subfolders based on file extension. The user selects (or drag-drops) a folder, previews the planned changes, then clicks **Organize Now** to move the files. It supports undo, statistics, and full settings control.

The app is built with **PyWebView** — a Python launcher (`pywebview_main.py`) opens a native desktop window that renders `app.html` as the UI. Python logic is exposed to JavaScript via `window.pywebview.api.*`.

---

## About the Design Files
The files in this bundle are **design references created in HTML** — high-fidelity prototypes showing the intended look, layout, and behaviour. They are not production code to copy directly.

Your task is to **recreate these HTML designs** using the existing Python + PyWebView architecture in this repo. The `app.html` file is already the real UI; `pywebview_api.py` is the real Python backend. Claude Code should implement, extend, and polish these files — not start from scratch.

---

## Fidelity
**High-fidelity.** The mockups use final colours, typography, spacing, and interactions. Implement pixel-accurately.

---

## Design Tokens

```
Background:     #f8f8f5   (warm off-white — body/page bg)
Surface:        #ffffff   (cards, nav, panels)
Surface 2:      #f2f2ef   (hover states, inputs, secondary bg)
Border:         #e4e4dc   (all dividers and card borders)
Text primary:   #1a1a17
Text secondary: #5c5c56
Text tertiary:  #9b9b93
Accent:         #1a6cf0   (primary blue — buttons, links, focus)
Accent hover:   #1459d0
Accent light:   #e8f0fe   (badge bg, active states)
Green:          #16a34a
Green light:    #dcfce7
Amber:          #d97706
Amber light:    #fef3c7
Red:            #dc2626
Red light:      #fee2e2

Font:           'Plus Jakarta Sans' (400, 500, 600, 700, 800)
Mono font:      'JetBrains Mono' (400, 500) — used for paths, code, ext map
Border radius:  12px standard · 10px buttons · 14px drop zone · 99px pills/badges
Shadow:         0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.04)
```

---

## File Architecture

```
pywebview_main.py    ← launcher — run this to open the app
pywebview_api.py     ← Python backend, all methods exposed to JS
app.html             ← full UI (HTML + CSS + JS in one file)
extension_map.txt    ← auto-created on first run
settings.json        ← auto-created on first run
operation_log.json   ← auto-created on first run
```

---

## Screens & Views

### 1. Home Screen (`#screen-home`)
The main screen. Always visible on launch.

**Layout:** Single column, `padding: 22px 24px`, `gap: 14px` between sections, scrollable.

#### Drop Zone
- Full-width card, `border: 2px dashed #e4e4dc`, `border-radius: 14px`, `padding: 36px 24px`, centred content
- On hover / drag-over: border → `#1a6cf0`, background → `#e8f0fe`, icon bg → `#1a6cf0` (white icon)
- Icon: 48×48px rounded square (`border-radius: 13px`), upload arrow SVG
- Title: 15px, 700 weight. Sub: 12px, `#9b9b93`. "browse" text: `#1a6cf0`, 600 weight
- Clicking anywhere calls `api.pick_folder()` via pywebview

#### Folder Strip (hidden until folder selected)
- Surface card, `border-radius: 12px`, `padding: 11px 16px`
- Left: 34×34px accent-light icon box + folder name (13px 600) + meta line (11px tertiary)
- Right: green pill badge "Ready" (`background: #dcfce7, color: #16a34a`)

#### Stat Cards (3-column grid, `gap: 10px`)
Each card: Surface, border, `border-radius: 12px`, `padding: 14px 15px`
- Emoji icon (18px), large number (22px 800), label (11px tertiary)
- Categories: Images 🖼, Documents 📄, Videos 🎬
- Values populated by `api.scan_folder()` after folder selection

#### Progress Bar
- Label: 12px tertiary. Track: 6px height, `#f2f2ef` bg, `border-radius: 99px`
- Fill: `#1a6cf0`, animates width on progress events. Indeterminate: CSS animation

#### Action Buttons Row
- Left: Preview btn + Undo btn (both secondary style, disabled until folder selected)
- Right: "Organize Now →" primary blue btn (`margin-left: auto`)
- Button style: `border-radius: 10px`, `padding: 9px 18px`, 13px 600 weight
- Primary: `background: #1a6cf0`, white text. Secondary: Surface bg, `border: 1px solid #e4e4dc`

---

### 2. Preview Screen (`#screen-preview`)
Shown when user clicks Preview. Full-height with sticky header.

**Header** (Surface bg, bottom border):
- Left: Title "Preview Changes" (16px 800) + subtitle with file count/size
- Right: Cancel + "Confirm & Organize" buttons
- Below: Row of pills (blue for counts/size, gray for categories, amber for skipped)

**File tree list** (scrollable, `padding: 12px 16px`):
- Each group: Surface card, `border-radius: 10px`
- Group header: folder emoji + name (13px 600) + file count + size + chevron `›`
- Click header to toggle open/closed (chevron rotates 90°)
- Expanded: file list indented, 12px secondary colour, prefixed with `·`
- First group open by default

**Footer** (Surface bg, top border): Cancel + Confirm buttons

---

### 3. Progress Screen (`#screen-progress`)
Shown while `api.organize()` runs. Centred layout, `padding: 32px 48px`.

- Icon: 60×60px `#e8f0fe` rounded square with folder+plus SVG in `#1a6cf0`
- Title: "Organizing files…" (20px 800). Sub: file count description
- Large progress bar: 8px height, gradient fill `linear-gradient(90deg, #1a6cf0, #5b8ff0)`
- Progress header: "X of Y files" left, "Z%" right
- Current file: 11px mono, tertiary colour, truncated
- Steps list (4 steps): Scanning → Creating folders → Moving files → Finishing up
  - Done: green filled circle with white checkmark
  - Active: accent-light circle with accent dot inside
  - Pending: plain border circle

**Progress events** arrive via `window.__bridge(jsonPayload)`:
```js
{ event: 'progress', data: { current, total, pct, file } }
{ event: 'done',     data: { moved, renamed, skipped, size_mb, master_folder, timestamp, can_undo } }
{ event: 'error',    data: { message } }
```

---

### 4. Complete Screen (`#screen-complete`)
Shown automatically ~600ms after `done` event. Centred layout.

- Icon: 60×60px `#dcfce7` rounded square, white checkmark in `#16a34a`
- Title: "Organization complete!" (22px 800)
- Sub: "All files have been sorted into **[master folder name]**"
- 4-column stat grid (same card style as home):
  - Files moved (green value), Renamed (accent), Skipped (amber), Total size (txt1)
- Output path bar: mono font 11px, folder icon left, "Open →" link-button right
  - Clicking "Open →" calls `api.open_folder_in_explorer(path)`
- Timestamp: 11px tertiary
- Buttons: Undo (secondary) + "Organize another folder" (primary)

---

### 5. Statistics Screen (`#screen-stats`)
Accessible via nav tab "Statistics". Calls `api.get_operation_logs()` on load.

**Top row** (4-column grid):
- Cards: Total runs (accent), Files organized (green), Total size, Last run date
- Values computed by aggregating `operation_log.json` entries

**Operation History** (Surface card, flex: 1):
- Header bar: "Operation History" (11px uppercase)
- Each row: green check icon box + folder path (mono 12px 600) + meta (11px tertiary) + date right-aligned
- Empty state: centred message if no logs

---

### 6. Settings Screen (`#screen-settings`)
Accessible via nav tab "Settings". Calls `api.get_settings()` and `api.get_ext_map_text()` on load.

**3 tabs:** General · Exclude Patterns · Extension Map
Tab bar style: bottom border indicator `#1a6cf0`, 2px. Inactive: `#9b9b93`.

**General tab:**
- **Output block:** master folder name — label left, text input right (220px, mono font, `#f2f2ef` bg)
- **Behavior block:** Recursive + Auto-organize — label/desc left, toggle switch right
  - Toggle: 36×20px pill, `#e4e4dc` off / `#1a6cf0` on, white knob slides left/right
- **Duplicates block:** 3-option selector (Rename / Skip / Overwrite)
  - Each option: flex card, `border-radius: 8px`, `border: 1.5px solid #e4e4dc`
  - Active: `border-color: #1a6cf0`, `background: #e8f0fe`

**Exclude Patterns tab:**
- Full-height textarea (mono font 12px, `#f2f2ef` bg, no border, `line-height: 1.8`)

**Extension Map tab:**
- Full-height textarea (same style), format hint in header

**Footer:** Cancel + "Save changes" buttons. Save calls `api.save_settings()` + `api.save_ext_map()`.

---

## Python API Reference (`pywebview_api.py`)

All methods are called from JS as `await window.pywebview.api.method_name(args)`.

| Method | Args | Returns |
|--------|------|---------|
| `pick_folder()` | — | `{path, name}` or `null` |
| `scan_folder(path)` | `str` | `{categories, total_files, total_size_mb}` |
| `preview_folder(path)` | `str` | `{groups, total_files, total_size_mb, skipped}` |
| `organize(path)` | `str` | Streams events via `window.__bridge()`, returns `{status}` |
| `undo()` | — | `{restored, failed, has_more}` |
| `get_operation_logs()` | — | `[{timestamp, source_folder, files_count, size_mb}]` |
| `get_settings()` | — | settings dict |
| `save_settings(dict)` | `dict` | `{status}` |
| `get_ext_map_text()` | — | raw string |
| `save_ext_map(text)` | `str` | `{status}` |
| `open_folder_in_explorer(path)` | `str` | `{status}` |

### Event bridge (Python → JS)
Python pushes real-time updates via:
```python
self._push("progress", { "current": i, "total": n, "pct": 63, "file": "photo.jpg" })
self._push("done", { "moved": 335, ... })
self._push("error", { "message": "..." })
```

JS receives them via:
```js
window.__bridge = (payload) => {
  const { event, data } = JSON.parse(payload);
  handlers[event]?.(data);
};
```

---

## Nav Structure
```
Top nav (sticky, 50px height, Surface bg):
  Left:  Logo box (26×26px, accent bg) + "FileType Organizer" title + "Pro" badge
  Centre: Tab buttons — Organizer · Statistics · Settings
  Right:  "by Kahilu Chipango" (11px tertiary)
```

Active tab: `background: #e8f0fe`, `color: #1a6cf0`, 600 weight, `border-radius: 7px`.
Nav bar has `-webkit-app-region: drag` so the user can drag the window.

---

## Interactions Summary

| Trigger | Action |
|---------|--------|
| Click drop zone / browse link | `api.pick_folder()` → OS folder dialog |
| Drag folder onto drop zone | `ondrop` event → `api.scan_folder()` |
| Click Preview | `api.preview_folder()` → switch to Preview screen |
| Click group header in Preview | Toggle open/close with chevron rotation |
| Click Confirm & Organize | `api.organize()` → switch to Progress screen |
| Progress events stream in | Update progress bar, step indicators, file label |
| `done` event fires | Auto-switch to Complete screen after 600ms |
| Click Undo (any screen) | `api.undo()` → toast confirmation → go to Home |
| Click Statistics tab | `api.get_operation_logs()` → populate history |
| Click Settings tab | `api.get_settings()` + `api.get_ext_map_text()` → populate form |
| Click Save in Settings | `api.save_settings()` + `api.save_ext_map()` → toast |
| Click "Open →" on Complete | `api.open_folder_in_explorer()` |
| Click "Organize another folder" | Reset home screen state |

---

## Toast Notifications
Fixed bottom-centre, slide up on show:
- Default: dark bg (`#1a1a17`)
- Success: `background: #16a34a`
- Error: `background: #dc2626`
- Auto-dismiss after 2.8s

---

## Build & Run

```bash
# Development
pip install pywebview
python pywebview_main.py

# Production build
pip install pyinstaller
pyinstaller --onefile --windowed \
  --add-data "app.html:." \
  --add-data "extension_map.txt:." \
  --name "FileTypeOrganizer" \
  pywebview_main.py
```

---

## What Claude Code Should Do

1. **Run the app** — `pip install pywebview && python pywebview_main.py` — confirm it opens
2. **Polish `app.html`** — match every pixel to the design tokens above
3. **Harden `pywebview_api.py`** — add error handling, edge cases, better logging
4. **Wire up drag-drop fully** — pywebview has its own drag-drop API, hook it into `onDrop`
5. **Add the Statistics dashboard category breakdown** — bar chart per category type
6. **Package with PyInstaller** — single `.exe` / `.app` that bundles `app.html`
7. **Test edge cases** — empty folders, permission errors, duplicate files, very long paths
