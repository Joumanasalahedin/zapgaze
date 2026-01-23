# ZapGaze

A revolutionary ADHD evaluation tool through advanced pupillometry technology using eye tracking and Go/No-Go task performance analysis.

## Overview

ZapGaze uses cutting-edge pupillometry technology to detect potential ADHD indicators through precise eye movement and pupil response analysis. Our non-invasive, scientifically-backed approach provides quick and accurate assessments that can help identify attention-related challenges early.

## 🚀 Live Application

**Access the deployed application:**

- **Web Application**: http://20.74.82.26:5173
- **Backend API**: http://20.74.82.26:8000

**To use the application:**

1. Visit the web application URL above
2. Download the ZapGaze Agent directly from within the application (the app will guide you through the download process)
3. The agent will automatically connect to the backend and enable eye tracking

## Architecture

The system consists of three main components:

- **Frontend Web Application** (Deployed on Azure VM at `http://20.74.82.26:5173`): Main user interface for the ADHD assessment
- **Backend API Server** (Deployed on Azure VM at `http://20.74.82.26:8000`): Main database and business logic
- **Local Agent Server** (`http://localhost:9000`): Eye tracking and camera operations (runs on user's local machine)

## Prerequisites

- Webcam for eye tracking
- Windows or macOS computer
- The ZapGaze Agent will be downloaded automatically when you start the assessment

## Setup Instructions

#### Step 1: Visit the Application
Go to http://20.74.82.26:5173 in your web browser.

#### Step 2: Download the Agent
1. When you start the assessment, the application will prompt you to download the ZapGaze Agent
2. Click "Download Agent" and select your platform (Windows or macOS)
3. The agent file will download automatically

#### Step 3: Install and Run the Agent

**For macOS:**
1. Unzip the downloaded `ZapGazeAgent.zip` file
2. Right-click on `ZapGazeAgent` and select "Open" (you may need to do this twice if macOS blocks it the first time)
3. **Important**: If macOS shows a security warning, go to:
   - **System Settings** → **Privacy & Security**
   - Scroll down to find "ZapGazeAgent" or look for a message about allowing the app
   - Click **"Allow"** or **"Open Anyway"** to permit the app to run
4. The agent will start and display: "Agent URL: http://localhost:9000"

**For Windows:**
1. Double-click `ZapGazeAgent.exe`
2. If Windows Defender shows a warning, click "More info" then "Run anyway"
3. The agent will start and display: "Agent URL: http://localhost:9000"

#### Step 4: Start Your Assessment
1. Return to the web application (http://20.74.82.26:5173)
2. Complete the intake questionnaire
3. Begin your ADHD evaluation

**Note**: Keep the agent running in the background while you complete your assessment. You can minimize the agent window, but don't close it.


## Troubleshooting

### Common Issues

1. **Agent Won't Start on macOS**
   - Go to **System Settings** → **Privacy & Security**
   - Look for "ZapGazeAgent" in the list and click **"Allow"**
   - If you don't see it, try right-clicking the app and selecting "Open" again
   - You may need to restart your computer after allowing the app

2. **Camera Access Denied**
   - Ensure your browser allows camera access
   - Check that no other application is using the camera
   - On macOS: Go to **System Settings** → **Privacy & Security** → **Camera** and ensure your browser is allowed

3. **Port Already in Use**
   - Another instance of the agent may be running
   - Close other instances or restart your computer
   - On macOS/Linux: `lsof -ti:9000 | xargs kill`
   - On Windows: Check Task Manager for `ZapGazeAgent.exe`

4. **Agent Not Connecting**
   - Ensure the agent is running and shows "Agent URL: http://localhost:9000"
   - Check your internet connection
   - Try restarting the agent

## Deployment

The application is deployed on Azure Virtual Machine:

- **Frontend**: http://20.74.82.26:5173
- **Backend**: http://20.74.82.26:8000
- **Agent**: Users download and run locally (connects to backend automatically)

The deployment uses Docker Compose to run the backend and frontend services. The local agent is packaged as a standalone executable using PyInstaller and distributed via GitHub Releases.

### Building the Agent Executable

To build a new version of the agent executable:

```bash
# macOS/Linux
cd agent
./build.sh

# Windows
cd agent
build.bat
```

The executable will be in the `dist/` directory. See `agent/BUILD.md` for detailed build instructions.

## Support

For support and questions, please contact joumanasalahedin@gmail.com or somtochukwumbuko@gmail.com

For issues with the agent or application, please open an issue on [GitHub](https://github.com/Joumanasalahedin/zapgaze/issues)
