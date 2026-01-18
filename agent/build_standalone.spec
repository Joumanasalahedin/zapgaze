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

# Add agent_config.py if it exists (contains embedded API key)
if (project_root / 'agent' / 'agent_config.py').exists():
    datas_list.append((str(project_root / 'agent' / 'agent_config.py'), 'agent'))
    print(f"Added agent_config.py with embedded API key")

# Collect all agent Python files explicitly
agent_py_files = []
agent_dir = project_root / 'agent'
for py_file in agent_dir.glob('*.py'):
    if py_file.name not in ['build_standalone.spec', '__init__.py']:  # Don't include spec or __init__ (handled separately)
        agent_py_files.append(str(py_file))
        print(f"Including agent file: {py_file.name}")

a = Analysis(
    [launcher_path] + agent_py_files,  # Include agent Python files
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
        'contextlib',  # For asynccontextmanager
        'app.acquisition.camera_manager',
        'app.acquisition.mediapipe_adapter',
        'app.acquisition.eye_tracker_adapter',
        'agent',  # Import the agent package
        'agent.local_agent',
        'agent.acquisition_client',
        'agent.launcher',
        'agent.setup_autostart',
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

