#!/usr/bin/env bash
# This script will start the Docker backend and frontend containers and the Local Acquisition Agent.

set -e

BUILD_FLAG=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--build]"
            exit 1
            ;;
    esac
done

cleanup() {
    echo -e "\n\n🛑 Shutting down services..."
    echo "Stopping Local Acquisition Agent..."
    # Kill any process on port 9000
    lsof -ti:9000 | xargs kill -9 2>/dev/null || true
    
    echo "Stopping Docker Compose services..."
    docker-compose down
    
    echo "✅ All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

if [ "$BUILD_FLAG" = true ]; then
    echo "[1/3] Starting backend and frontend services with Docker Compose (building images)..."
    docker-compose up -d --build
else
    echo "[1/3] Starting backend and frontend services with Docker Compose..."
    docker-compose up -d
fi

echo "Backend is up at http://localhost:8000"
echo "Frontend is up at http://localhost:5173"

echo "[2/3] Launching Local Acquisition Agent on http://localhost:9000..."
echo "Press Ctrl+C to stop all services"
uvicorn agent.local_agent:app --host 0.0.0.0 --port 9000
