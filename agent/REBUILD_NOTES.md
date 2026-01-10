# Rebuild Notes - MediaPipe Fix

## Issues Fixed

1. **Subprocess Issue**: Changed from subprocess to threading for standalone executable
2. **MediaPipe Models**: Added MediaPipe modules directory to PyInstaller bundle

## Changes Made

### 1. `agent/local_agent.py`
- Added threading support for standalone executable
- Detects if running as executable vs script
- Uses `run_acquisition()` function directly instead of subprocess

### 2. `agent/acquisition_client.py`
- Refactored to have `run_acquisition()` function that can be called directly
- Maintains backward compatibility with command-line usage

### 3. `agent/build_standalone.spec`
- Added MediaPipe modules directory to `datas` list
- This includes all `.binarypb` and `.tflite` model files

## Rebuild Instructions

```bash
# Activate virtual environment
source venv_mp/bin/activate

# Rebuild the executable
./agent/build.sh
```

## Testing After Rebuild

1. **Start Docker backend/frontend**:
   ```bash
   docker-compose up -d
   ```

2. **Run the new executable**:
   ```bash
   ./dist/ZapGazeAgent
   ```

3. **Test via frontend**: http://localhost:5173
   - Should be able to start calibration
   - Camera should work
   - Acquisition should start properly

4. **Verify status**:
   ```bash
   curl http://localhost:9000/status
   # Should show: {"status": "stopped"} when idle
   # Or {"status": "running", "mode": "thread"} when active
   ```

## Expected File Size

The executable will be larger (150-200MB) because it now includes:
- Python runtime
- All dependencies
- MediaPipe model files (.binarypb, .tflite)
- OpenCV libraries

This is normal and expected.

