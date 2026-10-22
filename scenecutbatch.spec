# -*- mode: python ; coding: utf-8 -*-

import sys

block_cipher = None

# Icono del ejecutable: .ico en Windows; en macOS/Linux PyInstaller no acepta
# .ico (macOS usa .icns), por lo que se deja sin icono en esas plataformas.
_exe_icon = "assets/logo.ico" if sys.platform == "win32" else None

a = Analysis(
    ['src/_entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[('assets/logo.png', 'assets')],
    hiddenimports=[
        'scenedetect',
        'scenedetect.scene_manager',
        'scenedetect.detectors',
        'scenedetect.frame_timecode',
        'scenedetect.video_splitter',
        'scenedetect.platform',
        'cv2',
        'numpy',
        'typer',
        'rich',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy ML/data science — not needed for a CLI video tool
        'torch', 'torchvision', 'torchaudio', 'torchtext', 'torchdata',
        'tensorflow', 'tensorflow_estimator', 'keras',
        'sklearn', 'scikit-learn',
        'pandas',
        'matplotlib', 'matplotlib.pyplot',
        'PIL', 'Pillow',
        'jupyter', 'jupyter_client', 'jupyter_core', 'nbformat', 'nbclient',
        'ipython', 'ipykernel', 'traitlets',
        'dask', 'distributed',
        'numba', 'llvmlite',
        'transformers', 'datasets', 'tokenizers',
        'scipy',
        'av',
        'decord',
        'moviepy',
        'imageio',
        'skimage',
        'wand',
        'pyarrow',
        'fastparquet',
        'xlrd', 'openpyxl',
        'psycopg2', 'mysql', 'pymysql', 'sqlite3',
        'boto3', 'botocore', 'google.cloud', 'azure',
        'requests', 'urllib3',  # not needed for offline CLI
        'flask', 'django', 'fastapi', 'uvicorn', 'starlette',
        'celery', 'redis',
        'pytest', 'pytest_cov',  # not needed at runtime
        'setuptools', 'pip', 'wheel',
    ],
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
    name='scenecutbatch',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_exe_icon,
)
