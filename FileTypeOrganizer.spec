# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pywebview_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app.html', '.'),
        ('extension_map.txt', '.'),
    ],
    hiddenimports=[
        'webview',
        'bottle',
        'proxy_tools',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FileTypeOrganizerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS app bundle
app = BUNDLE(
    exe,
    name='FileTypeOrganizerPro.app',
    icon=None,
    bundle_identifier='com.kahiluchipango.filetypeorganizer',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',
        'CFBundleName': 'FileType Organizer Pro',
        'CFBundleDisplayName': 'FileType Organizer Pro',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)
