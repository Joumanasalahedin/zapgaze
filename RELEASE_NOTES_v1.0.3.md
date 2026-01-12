# ZapGaze Agent v1.0.3 Release Notes

## What's New
- ✅ Fixed macOS app bundle to automatically open Terminal window
- ✅ Improved agent stop mechanism to properly release camera
- ✅ Enhanced heartbeat system for better agent-backend communication
- ✅ Fixed calibration point timeout issues
- ✅ Improved camera initialization flow
- ✅ Fixed `lifespan` definition order issue in PyInstaller bundle

## Installation

### Windows
1. Download `ZapGazeAgent.exe`
2. Double-click to run

### macOS
1. Download `ZapGazeAgent.app.zip`
2. Unzip the file
3. Right-click `ZapGazeAgent.app` and select "Open"
4. Click "Open" in the security dialog
5. Terminal will open automatically with the agent running

### Linux
1. Download `ZapGazeAgent`
2. Make executable: `chmod +x ZapGazeAgent`
3. Run: `./ZapGazeAgent`

## Configuration

The agent will connect to the backend at: `http://20.74.82.26:8000`

To change the backend URL, set the `BACKEND_URL` environment variable before running the agent.

## Technical Details

### Changes from v1.0.2
- Fixed `.app` bundle structure to use wrapper script that opens Terminal
- Improved camera release mechanism in `stop_acquisition` command
- Enhanced agent heartbeat to properly handle session stop signals
- Fixed calibration point execution with better timeout handling
- Moved `lifespan` function definition before FastAPI app creation
- Added `contextlib` to PyInstaller hidden imports

## Support

For issues or questions, please open an issue on GitHub.
