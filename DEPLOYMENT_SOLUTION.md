# ZapGaze Cloud Deployment Solution

## Overview

This document explains the **easiest solution** for deploying ZapGaze to the cloud while handling the local camera service requirement.

## The Challenge

The Local Acquisition Agent needs direct access to the user's camera hardware, which cannot run in a cloud container. We solve this by:

1. **Deploy backend + frontend to cloud** (standard Docker deployment)
2. **Users download and run a standalone executable** on their local machine

## Solution: Standalone Executable

### For Users (Super Simple!)

1. **Download** one file: `ZapGazeAgent.exe` (Windows) or `ZapGazeAgent` (Mac/Linux)
2. **Double-click** to run
3. **Done!** The agent starts and connects to the cloud backend

### For Developers

The solution includes:
- ✅ **Launcher script** (`agent/launcher.py`) - Simple Python script that starts the agent
- ✅ **Auto-start setup** (`agent/setup_autostart.py`) - Optional auto-start on login
- ✅ **Build configuration** (`agent/build_standalone.spec`) - PyInstaller config
- ✅ **Build scripts** (`agent/build.sh` / `agent/build.bat`) - One-command build

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Cloud (Azure/AWS)                              │
│  ┌─────────────┐     ┌─────────────┐          │
│  │  Frontend   │────▶│   Backend   │          │
│  │  (Docker)   │     │  (Docker)   │          │
│  └─────────────┘     └─────────────┘          │
└─────────────────────────────────────────────────┘
                          ▲
                          │ HTTPS
                          │
┌─────────────────────────────────────────────────┐
│  User's Local Machine                          │
│  ┌─────────────┐                               │
│  │ZapGazeAgent │  (Standalone executable)     │
│  │ Port 9000   │                               │
│  └─────────────┘                               │
│        │                                        │
│        ▼                                        │
│  ┌─────────────┐                               │
│  │   Camera    │                               │
│  │  Hardware   │                               │
│  └─────────────┘                               │
└─────────────────────────────────────────────────┘
```

## Implementation Steps

### Step 1: Build the Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
cd /path/to/zapgaze
./agent/build.sh  # macOS/Linux
# OR
agent\build.bat    # Windows
```

This creates `dist/ZapGazeAgent` (or `.exe` on Windows) - a single file that includes everything.

### Step 2: Test Locally

```bash
# Test the executable
./dist/ZapGazeAgent

# Test auto-start setup (optional)
./dist/ZapGazeAgent --setup-autostart
```

### Step 3: Deploy Backend/Frontend to Cloud

Deploy your Docker containers to Azure or AWS as usual. The backend should:
- Accept connections from the frontend domain
- Accept data from user's local agents (via HTTPS)

### Step 4: Configure Agent for Cloud Backend

Users set the backend URL when running:
```bash
# macOS/Linux
export BACKEND_URL=https://your-backend.azurewebsites.net
./ZapGazeAgent

# Windows
set BACKEND_URL=https://your-backend.azurewebsites.net
ZapGazeAgent.exe
```

Or you can hardcode it in the launcher for your specific deployment.

### Step 5: Distribute to Users

- **Option A**: Direct download link (simplest)
- **Option B**: Installer package (more professional)
- **Option C**: Auto-updater (advanced)

## User Experience Flow

1. User visits your cloud-hosted web app
2. Web app detects if agent is running (checks `http://localhost:9000/status`)
3. If not running, shows download link: "Download ZapGaze Agent"
4. User downloads and runs the executable
5. Agent starts automatically
6. Web app connects to agent and starts the test

## Benefits

✅ **Easiest for users**: Just download and double-click  
✅ **Easiest to implement**: Uses existing Python code, minimal changes  
✅ **No dependencies**: Executable includes everything (Python, libraries, etc.)  
✅ **Cross-platform**: Works on Windows, Mac, Linux  
✅ **Optional auto-start**: Users can enable auto-start on login  

## File Sizes

The executable will be **100-200MB** because it includes:
- Python runtime
- OpenCV
- MediaPipe
- FastAPI
- All dependencies

This is normal and expected for PyInstaller with scientific libraries.

## Security Considerations

1. **Code signing**: Sign executables for distribution (prevents security warnings)
2. **HTTPS**: All communication between agent and cloud backend should use HTTPS
3. **CORS**: Configure backend CORS to only allow your frontend domain
4. **Authentication**: Consider adding API keys for agent-backend communication

## Next Steps

1. ✅ Build the executable using the provided scripts
2. ✅ Test locally with cloud backend URL
3. ✅ Deploy backend/frontend to cloud
4. ✅ Create download page for users
5. ✅ Add agent detection in frontend
6. ✅ Set up code signing (for production)

## Files Created

- `agent/launcher.py` - Main launcher script
- `agent/setup_autostart.py` - Auto-start configuration
- `agent/build_standalone.spec` - PyInstaller configuration
- `agent/build.sh` / `agent/build.bat` - Build scripts
- `agent/README_USER.md` - User documentation
- `agent/BUILD.md` - Developer build instructions

## Testing Checklist

- [ ] Build executable successfully
- [ ] Executable runs and starts agent on port 9000
- [ ] Agent connects to cloud backend
- [ ] Camera access works
- [ ] Auto-start setup works (optional)
- [ ] Frontend can detect agent running
- [ ] End-to-end test: User downloads → runs → completes test

