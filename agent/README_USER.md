# ZapGaze Local Agent - User Guide

## Quick Start

### Option 1: Standalone Executable (Easiest)

1. **Download** the executable for your platform:
   - macOS: `ZapGazeAgent` (or `ZapGazeAgent.app`)
   - Windows: `ZapGazeAgent.exe`
   - Linux: `ZapGazeAgent`

2. **Run** the executable:
   - **macOS/Linux**: Double-click or run from terminal: `./ZapGazeAgent`
   - **Windows**: Double-click `ZapGazeAgent.exe`

3. **Verify** it's running:
   - You should see: "Agent URL: http://localhost:9000"
   - The agent is ready when you see "Application startup complete"

4. **Optional - Auto-start on login**:
   - Run: `./ZapGazeAgent --setup-autostart` (or use the setup script)
   - The agent will start automatically when you log in

### Option 2: Python Script (If you have Python installed)

1. **Install dependencies**:
```bash
pip install -r requirements_local.txt
```

2. **Run the launcher**:
```bash
python agent/launcher.py
```

3. **Set up auto-start** (optional):
```bash
python agent/setup_autostart.py
```

## Configuration

### Backend URL

By default, the agent connects to `http://localhost:8000`. 

To change this, set the `BACKEND_URL` environment variable:

**macOS/Linux:**
```bash
export BACKEND_URL=https://your-backend-url.com
./ZapGazeAgent
```

**Windows:**
```cmd
set BACKEND_URL=https://your-backend-url.com
ZapGazeAgent.exe
```

## Troubleshooting

### Port 9000 Already in Use

If you see "Port 9000 is already in use":
- Another instance of the agent may be running
- Close other instances or restart your computer
- On macOS/Linux: `lsof -ti:9000 | xargs kill`
- On Windows: Check Task Manager for `ZapGazeAgent.exe`

### Camera Not Working

1. **Grant camera permissions**:
   - **macOS**: System Preferences > Security & Privacy > Camera
   - **Windows**: Settings > Privacy > Camera
   - **Linux**: May need to add user to `video` group

2. **Check camera is not in use**:
   - Close other applications using the camera (Zoom, Teams, etc.)

3. **Test camera access**:
   - Try opening the camera in another app first

### Agent Won't Start

1. **Check Python dependencies** (if using Python script):
   ```bash
   pip install -r requirements_local.txt
   ```

2. **Check firewall settings**:
   - Ensure port 9000 is not blocked
   - The agent only listens on localhost, so it's safe

3. **Check logs**:
   - Look for error messages in the console
   - On macOS with auto-start: `~/Library/Logs/zapgaze-agent.log`

## Stopping the Agent

- **If running in terminal**: Press `Ctrl+C`
- **If running in background**: 
  - **macOS**: `launchctl unload ~/Library/LaunchAgents/com.zapgaze.agent.plist`
  - **Windows**: Remove from Startup folder or Task Manager
  - **Linux**: `systemctl --user stop zapgaze-agent.service`

## Uninstalling Auto-start

**macOS:**
```bash
rm ~/Library/LaunchAgents/com.zapgaze.agent.plist
launchctl unload ~/Library/LaunchAgents/com.zapgaze.agent.plist
```

**Windows:**
- Delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ZapGazeAgent.bat`

**Linux:**
```bash
systemctl --user disable zapgaze-agent.service
rm ~/.config/systemd/user/zapgaze-agent.service
rm ~/.config/autostart/zapgaze-agent.desktop
```

## Support

For issues or questions, please contact support or check the main project documentation.

