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
2. Download and run the ZapGaze Agent for your platform (Windows/macOS) from [GitHub Releases](https://github.com/Joumanasalahedin/zapgaze/releases)
3. The agent will automatically connect to the backend and enable eye tracking

## Architecture

The system consists of three main components:

- **Frontend Web Application** (Deployed on Azure VM at `http://20.74.82.26:5173`): Main user interface for the ADHD assessment
- **Backend API Server** (Deployed on Azure VM at `http://20.74.82.26:8000`): Main database and business logic
- **Local Agent Server** (`http://localhost:9000`): Eye tracking and camera operations (runs on user's local machine)

## Prerequisites

### For End Users (Using the Deployed Application)

- Webcam for eye tracking
- Windows or macOS computer
- Download ZapGaze Agent from [GitHub Releases](https://github.com/Joumanasalahedin/zapgaze/releases)

### For Developers (Local Development)

- Python 3.8 or higher
- Webcam for eye tracking
- Docker

## Setup Instructions

### For End Users

1. **Visit the Application**: Go to http://20.74.82.26:5173
2. **Download the Agent**:
   - Click "Download Agent" on the homepage
   - Select your platform (Windows or macOS)
   - Download the executable from GitHub Releases
3. **Run the Agent**:
   - **Windows**: Double-click `ZapGazeAgent.exe`
   - **macOS**: Unzip `ZapGazeAgent.zip`, right-click `ZapGazeAgent` and select "Open"
4. **Start Assessment**: Once the agent is running, return to the web application and begin your assessment

### For Developers (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Joumanasalahedin/zapgaze
cd zapgaze

# Switch to the local branch for development
git checkout local
```

### 2. Local Agent Setup

#### Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Install Python Dependencies

```bash
# Install requirements
pip install -r requirements_local.txt
```

## Running the Application

### Option 1: Using the Start Script (preferred option)

```bash
# Make the script executable (macOS/Linux)
chmod +x start_app.sh

# Run the application (uses existing Docker images)
./start_app.sh

# Or run with --build flag to rebuild Docker images
./start_app.sh --build
```

### Option 2: Manual Startup

#### Terminal 1: Backend + Frontend (Docker)

```bash
docker-compose up --build
```

#### Terminal 2: Local Agent Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the local agent
cd agent
uvicorn local_agent:app --reload --host 0.0.0.0 --port 9000
```

### 3. Access the Application

Once all services are running, open your web browser and navigate to:

```
http://localhost:5173
```

This will open the ZapGaze web application where you can:

- Complete the intake process
- Run the ADHD assessment
- View your results

**Note**: For production use, visit the deployed application at http://20.74.82.26:5173

## Testing the Setup

### 1. Health Check

```bash
# Test backend API
curl http://localhost:8000/

# Test local agent
curl http://localhost:9000/status
```

### 2. Run Full Test Suite

```bash
# Make the test script executable
chmod +x test.sh

# Run the complete test
./test.sh
```

This will test:

- User intake and session creation
- Calibration process
- Eye tracking data acquisition
- Task event logging
- Feature computation
- Results retrieval

## API Endpoints

### Backend API (Production: `http://20.74.82.26:8000` | Local: `http://localhost:8000`)

#### Core Endpoints

- `POST /intake/` - Create user and session
- `POST /session/start` - Start session
- `POST /session/stop` - Stop session
- `POST /session/event` - Log task events

#### Data Endpoints

- `POST /acquisition/data` - Single eye tracking sample
- `POST /acquisition/batch` - Batch eye tracking samples
- `GET /results/{session_uid}` - Get raw results
- `DELETE /results/{session_uid}` - Delete raw results

#### Analysis Endpoints

- `POST /features/compute/{session_uid}` - Compute session features
- `GET /features/sessions/{session_uid}` - Get computed features
- `POST /session/{session_uid}/calibration/point` - Store calibration point
- `GET /session/{session_uid}/calibration` - Get calibration points

### Local Agent (`http://localhost:9000` - runs on user's machine)

#### Camera Operations

- `POST /calibrate/start` - Start calibration
- `POST /calibrate/point` - Capture calibration point
- `POST /calibrate/finish` - Finish calibration
- `POST /start` - Start eye tracking
- `POST /stop` - Stop eye tracking
- `GET /status` - Check agent status

## Development

### Project Structure

```
zapgaze/
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── db/                # Database models and setup
│   ├── models/            # Pydantic models
│   └── main.py            # FastAPI application
├── agent/                 # Local agent for eye tracking
│   ├── acquisition_client.py
│   ├── local_agent.py
│   └── task_manager.py
├── frontend/              # React frontend (containerized)
│   ├── src/
│   ├── package.json
│   ├── Dockerfile
│   └── ...
├── requirements_local.txt # Python dependencies
├── docker-compose.yml     # Docker orchestration
├── test.sh               # Test script
└── start_app.sh          # Startup script
```

### Key Features

- **Session-based Architecture**: Uses `session_uid` as primary identifier
- **Real-time Eye Tracking**: MediaPipe-based face and eye detection
- **Go/No-Go Task**: Standard attention assessment protocol
- **Feature Computation**: Automatic calculation of ADHD indicators
- **Modern Web Interface**: React-based user experience (containerized)

## Troubleshooting

### Common Issues

1. **Camera Access Denied**

   - Ensure your browser allows camera access
   - Check that no other application is using the camera

2. **Port Already in Use**

   - Kill processes using ports 8000, 9000, or 5173
   - Or change ports in the respective configuration files

3. **MediaPipe Installation Issues**

   - Ensure you have Python 3.8+ installed
   - Try reinstalling: `pip uninstall mediapipe && pip install mediapipe`

4. **Database Errors**

   - Delete `zapgaze.db` file and restart the application
   - The database will be recreated automatically

5. **Docker Issues**
   - Ensure Docker is running
   - Try rebuilding containers: `docker-compose build --no-cache`

### Logs

- Backend logs: Check Docker logs with `docker-compose logs backend`
- Local agent logs: Check terminal running the local agent
- Frontend logs: Check Docker logs with `docker-compose logs frontend`

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
