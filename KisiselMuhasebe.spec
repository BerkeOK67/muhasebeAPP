# PyInstaller spec - Kişisel Muhasebe EXE
# Kullanım: pyinstaller KisiselMuhasebe.spec
# Gereksinim: pip install pyinstaller waitress

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
root = os.path.dirname(os.path.abspath(SPEC))

# Datas listesi oluştur
datas_list = [
    (os.path.join(root, 'app', 'templates'), 'app/templates'),
    (os.path.join(root, 'app', 'static'), 'app/static'),
    (os.path.join(root, 'config.py'), '.'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[root],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'app', 'app.main', 'app.gelirler', 'app.giderler', 'app.alacaklilar', 'app.gelisim',
        'app.license_check', 'app.firebase_licenses', 'app.firebase_admin',
        'config', 'waitress', 'flask', 'pytz', 'firebase_admin', 'werkzeug',
        'firebase_admin.credentials', 'firebase_admin.db',
        'google.auth', 'google.auth.transport', 'google.auth.transport.requests',
        'google.oauth2', 'cachetools', 'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['admin_app'],
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
    name='KisiselMuhasebe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
