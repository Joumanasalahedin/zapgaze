# Building Standalone Executable for ZapGaze Agent

This guide explains how to build a standalone executable that users can download and run without installing Python.

## Prerequisites

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Install all dependencies:
```bash
pip install -r requirements_local.txt
```

## Building the Executable

### Option 1: Using the Spec File (Recommended)

```bash
cd /path/to/zapgaze
pyinstaller agent/build_standalone.spec
```

The executable will be in `dist/ZapGazeAgent` (or `dist/ZapGazeAgent.exe` on Windows).

### Option 2: Quick Build Command

```bash
cd /path/to/zapgaze
pyinstaller --name ZapGazeAgent \
    --add-data "agent/calibration.json:agent" \
    --hidden-import uvicorn \
    --hidden-import fastapi \
    --hidden-import mediapipe \
    --hidden-import cv2 \
    --hidden-import app.acquisition.camera_manager \
    --hidden-import app.acquisition.mediapipe_adapter \
    --hidden-import agent.local_agent \
    --onefile \
    agent/launcher.py
```

## Platform-Specific Notes

### macOS
- The executable will be `dist/ZapGazeAgent`
- You may need to sign it for distribution: `codesign --sign "Developer ID" dist/ZapGazeAgent`
- Users may need to allow it in System Preferences > Security

### Windows
- The executable will be `dist/ZapGazeAgent.exe`
- May trigger Windows Defender warnings (false positive)
- Consider code signing for production

### Linux
- The executable will be `dist/ZapGazeAgent`
- Make it executable: `chmod +x dist/ZapGazeAgent`
- May need to install system dependencies: `sudo apt-get install libgl1-mesa-glx libgstreamer1.0-0`

## File Size

The executable will be large (100-200MB) because it includes:
- Python runtime
- All dependencies (OpenCV, MediaPipe, FastAPI, etc.)
- All Python libraries

This is normal for PyInstaller executables with scientific libraries.

## Testing

1. Test the executable locally:
```bash
./dist/ZapGazeAgent
```

2. Test auto-start setup:
```bash
python agent/setup_autostart.py
```

3. Verify it starts on port 9000:
```bash
curl http://localhost:9000/status
```

## Distribution

1. **For macOS**: Create a `.dmg` file or zip the executable
2. **For Windows**: Create an installer (using Inno Setup or NSIS) or zip the `.exe`
3. **For Linux**: Create a `.deb` or `.rpm` package, or distribute as a tar.gz

## Troubleshooting

### "Module not found" errors
- Add missing modules to `hiddenimports` in the spec file
- Use `--collect-all <module>` for packages with submodules

### Camera access issues
- On macOS: May need to grant camera permissions in System Preferences
- On Linux: May need to add user to `video` group: `sudo usermod -a -G video $USER`

### Large file size
- This is expected with MediaPipe and OpenCV
- Consider using UPX compression (already enabled in spec file)

