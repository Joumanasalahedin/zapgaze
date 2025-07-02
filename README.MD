# ZapGaze

A revolutionary ADHD detection tool through advanced pupillometry technology using eye tracking and Go/No-Go task performance analysis.

## Overview

ZapGaze uses cutting-edge pupillometry technology to detect potential ADHD indicators through precise eye movement and pupil response analysis. Our non-invasive, scientifically-backed approach provides quick and accurate assessments that can help identify attention-related challenges early.

## Architecture

The system consists of three main components:

- **Frontend Web Application** (`http://localhost:5173`): Main user interface for the ADHD assessment
- **Backend API Server** (`http://localhost:8000`): Main database and business logic
- **Local Agent Server** (`http://localhost:9000`): Eye tracking and camera operations

## Prerequisites

- Python 3.8 or higher
- Webcam for eye tracking
- Docker

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Joumanasalahedin/zapgaze
cd zapgaze
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

### Backend API (`http://localhost:8000`)

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

### Local Agent (`http://localhost:9000`)

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

## Support

For support and questions, please contact joumanasalahedin@gmail.com or somtochukwumbuko@gmail.com
