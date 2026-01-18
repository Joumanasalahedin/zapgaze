# ZapGaze Agent v1.0.4 Release Notes

## What's New

### 🔒 Enhanced API Validation & Type Safety
- ✅ **Comprehensive Pydantic validation** for all API endpoints
- ✅ **Field constraints** on request parameters (FPS limits, coordinate validation, sample counts)
- ✅ **Type checking** with return type hints for better IDE support
- ✅ **Business logic validation** (calibration state checks, session validation)
- ✅ **Improved error messages** with clear validation feedback

### 🛡️ Backend API Improvements
- ✅ **Structured request models** for agent heartbeat, calibration, and acquisition endpoints
- ✅ **Automatic validation** of API request formats
- ✅ **Prevents API failures** from malformed data

### 📝 Code Quality
- ✅ **Type hints** added to all endpoint functions
- ✅ **Better error handling** with descriptive messages
- ✅ **Improved code maintainability**

## Installation

### macOS
1. Download `ZapGazeAgent.zip`
2. Unzip the file
3. Make executable: `chmod +x ZapGazeAgent`
4. Run: `./ZapGazeAgent`

**Note:** On first run, macOS may show a security warning. To allow:
- Right-click the file and select "Open"
- Click "Open" in the security dialog
- Or go to System Preferences > Security & Privacy > General and click "Open Anyway"

## Configuration

The agent will connect to the backend at: `http://20.74.82.26:8000`

To change the backend URL, set the `BACKEND_URL` environment variable before running:
```bash
export BACKEND_URL=http://your-backend-url:8000
./ZapGazeAgent
```

## Technical Details

### Validation Improvements

**Agent Local API (`agent/local_agent.py`):**
- `StartRequest`: Validates `session_uid` (min length), `api_url` (URL pattern), `fps` (0-120 range)
- `CalPointRequest`: Validates coordinates (≥0), `duration` (0-10s), `samples` (1-1000)
- Business logic: Checks calibration state before processing points
- Return type hints: All endpoints now have `-> Dict[str, Any]`

**Backend Agent API (`app/api/agent.py`):**
- `AgentHeartbeat`: Now uses Pydantic model instead of raw dict
- `CalibrationPointRequest`: New model with field constraints
- `StartAcquisitionRequest`: New model with URL pattern and FPS validation
- All endpoints: Return type hints added

### Breaking Changes
**None** - All changes are backward compatible. Existing API calls will continue to work, but now with better validation.

### Migration Notes
No migration needed. The agent will work with existing backends and frontends. The validation improvements are transparent to users.

## Changes from v1.0.3

### Added
- Pydantic Field constraints on all request models
- Type hints for all API endpoints
- Business logic validation (calibration state checks)
- Structured request models for backend agent API

### Improved
- Error messages are more descriptive
- API request validation prevents malformed data
- Code maintainability with type hints

### Fixed
- None (this is a feature release)

## Support

For issues or questions, please open an issue on [GitHub](https://github.com/Joumanasalahedin/zapgaze/issues).

## Download

**macOS:**
- Download: `ZapGazeAgent.zip`
- Size: ~150-200MB (includes Python runtime and all dependencies)

## Build Information

- Built with: PyInstaller
- Python version: 3.10
- Dependencies: FastAPI, Pydantic, MediaPipe, OpenCV, NumPy
