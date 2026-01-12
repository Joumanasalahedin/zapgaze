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
    
    # For macOS, create a zip file with execute permissions preserved
    if [ -f "dist/ZapGazeAgent" ] && [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Creating zip file with execute permissions..."
        
        # Ensure executable has permissions
        chmod +x "dist/ZapGazeAgent"
        
        # Create a temporary directory with the executable
        TEMP_DIR=$(mktemp -d)
        cp "dist/ZapGazeAgent" "$TEMP_DIR/"
        chmod +x "$TEMP_DIR/ZapGazeAgent"
        
        # Create zip file for GitHub Releases (preserves permissions)
        ZIP_NAME="ZapGazeAgent.zip"
        cd "$TEMP_DIR"
        # Use zip -X to exclude extra attributes, but keep permissions
        zip -X "$PROJECT_ROOT/dist/$ZIP_NAME" ZapGazeAgent > /dev/null
        cd "$PROJECT_ROOT"
        
        # Clean up temp directory
        rm -rf "$TEMP_DIR"
        
        echo "✅ Created zip file: dist/$ZIP_NAME"
        echo ""
        echo "Executable locations:"
        echo "  dist/ZapGazeAgent (standalone)"
        echo "  dist/$ZIP_NAME (for GitHub release)"
        echo ""
        echo "File sizes:"
        ls -lh dist/ZapGazeAgent "dist/$ZIP_NAME"
        echo ""
        echo "To test standalone:"
        echo "  ./dist/ZapGazeAgent"
        echo ""
        echo "For GitHub release, upload: dist/$ZIP_NAME"
        echo "   Users should unzip it and run: ./ZapGazeAgent"
    else
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
    fi
else
    echo ""
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi

