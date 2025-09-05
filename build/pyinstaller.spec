# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None


def get_spec():
    import sys
    from PyInstaller.utils.hooks import collect_submodules

    pathex = [str(Path('.').resolve()), str(Path('src').resolve())]

    # Hidden imports sometimes needed on Windows for tray/backends
    hiddenimports = []

    # Incluir icono de assets en el paquete si existe
    datas_list = []
    # Incluir todos los .ico de assets
    assets_dir = Path('assets').resolve()
    if assets_dir.exists():
        for ico in assets_dir.glob('*.ico'):
            datas_list.append((str(ico), 'assets'))

    a = Analysis(
        [str(Path('src/main.py').resolve())],
        pathex=pathex,
        binaries=[],
        datas=datas_list,
        hiddenimports=hiddenimports,
        hookspath=[],
        hooksconfig={},
        runtime_hooks=[],
        excludes=[],
        noarchive=False,
    )
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='FichajeTray',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # ventana oculta (tipo pythonw)
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=str(next(assets_dir.glob('*.ico'), None)) if assets_dir.exists() and any(assets_dir.glob('*.ico')) else None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='FichajeTray'
    )
    return coll


coll = get_spec()


