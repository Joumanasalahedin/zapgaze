# PyInstaller spec file for ZapGaze Local Agent
# Usage: pyinstaller agent/build_standalone.spec
# Note: Must be run from project root directory

import sys
import os
from pathlib import Path

# Get project root from current working directory (build script runs from project root)
project_root = Path.cwd()

# Use absolute path for the launcher script
launcher_path = str(project_root / 'agent' / 'launcher.py')

# Verify the file exists
if not os.path.exists(launcher_path):
    raise FileNotFoundError(f"Launcher script not found at: {launcher_path}\nCurrent directory: {project_root}")

# Collect MediaPipe data files
datas_list = []
try:
    import mediapipe
    mediapipe_path = Path(mediapipe.__file__).parent
    # Collect all MediaPipe modules directory (contains .binarypb and .tflite files)
    mediapipe_modules = mediapipe_path / 'modules'
    if mediapipe_modules.exists():
        # Add the entire modules directory
        datas_list.append((str(mediapipe_modules), 'mediapipe/modules'))
        print(f"Added MediaPipe modules: {mediapipe_modules}")
except Exception as e:
    print(f"Warning: Could not find MediaPipe modules: {e}")

# Add calibration.json if it exists
if (project_root / 'agent' / 'calibration.json').exists():
    datas_list.append((str(project_root / 'agent' / 'calibration.json'), 'agent'))

a = Analysis(
    [launcher_path],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'numpy',
        'cv2',
        'mediapipe',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solutions.drawing_utils',
        'app.acquisition.camera_manager',
        'app.acquisition.mediapipe_adapter',
        'app.acquisition.eye_tracker_adapter',
        'agent.local_agent',
        'agent.acquisition_client',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ZapGazeAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

