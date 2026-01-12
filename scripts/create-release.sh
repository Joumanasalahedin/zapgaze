#!/usr/bin/env bash
# Script to help create GitHub releases for ZapGaze Agent
# Usage: ./scripts/create-release.sh v1.0.3

set -e

VERSION=${1:-v1.0.3}
REPO="Joumanasalahedin/zapgaze"

echo "=========================================="
echo "Creating GitHub Release: $VERSION"
echo "=========================================="
echo ""

# Check if executables exist, build if needed
if [ ! -f "dist/ZapGazeAgent" ] && [ ! -f "dist/ZapGazeAgent.app.zip" ]; then
    echo "❌ Executables not found. Building first..."
    ./agent/build.sh
fi

echo "Files ready for release:"
if [ -f "dist/ZapGazeAgent.exe" ]; then
    echo "  ✅ Windows: dist/ZapGazeAgent.exe ($(ls -lh dist/ZapGazeAgent.exe | awk '{print $5}'))"
fi
if [ -f "dist/ZapGazeAgent.app.zip" ]; then
    echo "  ✅ macOS: dist/ZapGazeAgent.app.zip ($(ls -lh dist/ZapGazeAgent.app.zip | awk '{print $5}'))"
fi
if [ -f "dist/ZapGazeAgent" ]; then
    echo "  ✅ Linux: dist/ZapGazeAgent ($(ls -lh dist/ZapGazeAgent | awk '{print $5}'))"
fi
echo ""

# Generate release notes
RELEASE_NOTES="## ZapGaze Agent $VERSION

### What's New
- Fixed macOS app bundle to automatically open Terminal window
- Improved agent stop mechanism to properly release camera
- Enhanced heartbeat system for better agent-backend communication
- Fixed calibration point timeout issues
- Improved camera initialization flow

### Installation

**Windows:**
1. Download \`ZapGazeAgent.exe\`
2. Double-click to run

**macOS:**
1. Download \`ZapGazeAgent.app.zip\`
2. Unzip the file
3. Right-click \`ZapGazeAgent.app\` and select \"Open\"
4. Click \"Open\" in the security dialog
5. Terminal will open automatically with the agent running

**Linux:**
1. Download \`ZapGazeAgent\`
2. Make executable: \`chmod +x ZapGazeAgent\`
3. Run: \`./ZapGazeAgent\`

### Configuration

The agent will connect to the backend at: \`http://20.74.82.26:8000\`

To change the backend URL, set the \`BACKEND_URL\` environment variable before running the agent.

### Support

For issues or questions, please open an issue on GitHub."

echo "=========================================="
echo "Release Notes (copy this to GitHub):"
echo "=========================================="
echo ""
echo "$RELEASE_NOTES"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Go to: https://github.com/$REPO/releases/new"
echo "2. Tag version: $VERSION"
echo "3. Title: ZapGaze Agent $VERSION"
echo "4. Paste the release notes above"
echo "5. Upload files:"
if [ -f "dist/ZapGazeAgent.exe" ]; then
    echo "   - dist/ZapGazeAgent.exe"
fi
if [ -f "dist/ZapGazeAgent.app.zip" ]; then
    echo "   - dist/ZapGazeAgent.app.zip"
fi
if [ -f "dist/ZapGazeAgent" ]; then
    echo "   - dist/ZapGazeAgent (rename to ZapGazeAgent-linux if needed)"
fi
echo "6. Publish release"
echo ""
echo "Download URLs after publishing:"
if [ -f "dist/ZapGazeAgent.exe" ]; then
    echo "  Windows: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent.exe"
fi
if [ -f "dist/ZapGazeAgent.app.zip" ]; then
    echo "  macOS: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent.app.zip"
fi
if [ -f "dist/ZapGazeAgent" ]; then
    echo "  Linux: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent"
fi
echo ""

