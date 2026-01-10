#!/usr/bin/env bash
# Build script for ZapGaze Agent standalone executable

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Building ZapGaze Agent Standalone"
echo "=========================================="
echo ""

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller is not installed."
    echo "   Installing PyInstaller..."
    pip install pyinstaller
fi

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Not in a virtual environment."
    echo "   It's recommended to use a virtual environment."
    read -p "Continue anyway? (y/n): " response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Install/update dependencies
echo "Installing dependencies..."
cd "$PROJECT_ROOT"
pip install -r requirements_local.txt

# Build the executable
echo ""
echo "Building executable..."
cd "$PROJECT_ROOT"
pyinstaller agent/build_standalone.spec --clean

# Check if build was successful
if [ -f "dist/ZapGazeAgent" ] || [ -f "dist/ZapGazeAgent.exe" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Build successful!"
    echo "=========================================="
    echo ""
    echo "Executable location:"
    if [ -f "dist/ZapGazeAgent" ]; then
        echo "  dist/ZapGazeAgent"
        chmod +x dist/ZapGazeAgent
    fi
    if [ -f "dist/ZapGazeAgent.exe" ]; then
        echo "  dist/ZapGazeAgent.exe"
    fi
    echo ""
    echo "File size:"
    ls -lh dist/ZapGazeAgent* 2>/dev/null || ls -lh dist/ZapGazeAgent.exe
    echo ""
    echo "To test:"
    echo "  ./dist/ZapGazeAgent"
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi

