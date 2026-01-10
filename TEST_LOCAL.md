# Testing Standalone Executable with Local Docker Backend

## Quick Test Guide

### Step 1: Start Docker Backend and Frontend

Start only the backend and frontend (not the local agent, since we'll use the standalone executable):

```bash
# Start Docker services
docker-compose up -d

# Verify they're running
docker-compose ps

# Check backend is accessible
curl http://localhost:8000/
# Should return: {"message":"ZapGaze API is running."}

# Frontend should be at http://localhost:5173
```

### Step 2: Run the Standalone Executable

The executable defaults to `http://localhost:8000`, so you can run it directly:

```bash
# From the project root
./dist/ZapGazeAgent
```

You should see:
```
==================================================
ZapGaze Local Agent
==================================================
Backend URL: http://localhost:8000
Agent URL: http://localhost:9000
==================================================

Starting agent...
Press Ctrl+C to stop
```

### Step 3: Verify Agent is Running

In another terminal, test the agent:

```bash
# Check agent status
curl http://localhost:9000/status
# Should return: {"status":"stopped"} (or "running" if acquisition is active)
```

### Step 4: Test Full Flow

1. **Open frontend**: http://localhost:5173
2. **Frontend should detect agent** at `http://localhost:9000`
3. **Start a test session** - the agent should connect to backend at `http://localhost:8000`
4. **Verify data flow**: Agent → Backend → Database

### Step 5: Test with Custom Backend URL (Optional)

If you want to test pointing to a different backend:

```bash
BACKEND_URL=http://localhost:8000 ./dist/ZapGazeAgent
```

## Troubleshooting

### Port 9000 Already in Use
If you see "Port 9000 is already in use":
- You might have the old agent running from `start_app.sh`
- Stop it: `lsof -ti:9000 | xargs kill -9`
- Or use the standalone executable instead

### Backend Not Found
- Verify Docker is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Verify backend is accessible: `curl http://localhost:8000/`

### Agent Can't Connect to Backend
- Make sure backend is running: `docker-compose up -d`
- Check backend URL in agent output (should be `http://localhost:8000`)
- Verify no firewall blocking localhost connections

## Testing Checklist

- [ ] Docker backend is running on port 8000
- [ ] Docker frontend is running on port 5173
- [ ] Standalone executable runs without errors
- [ ] Agent is accessible at http://localhost:9000/status
- [ ] Frontend can connect to agent
- [ ] Agent can send data to backend
- [ ] End-to-end test completes successfully

