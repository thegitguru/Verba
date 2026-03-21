# verba-linux.spec
# Build with: pyinstaller verba-linux.spec

from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['verba_main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules('verba'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='verba',
    debug=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    target_arch=None,
)
