#!/usr/bin/env bash
# Script to help create GitHub releases for ZapGaze Agent
# Usage: ./scripts/create-release.sh v1.0.4

set -e

VERSION=${1:-v1.0.5}
REPO="Joumanasalahedin/zapgaze"

echo "=========================================="
echo "Creating GitHub Release: $VERSION"
echo "=========================================="
echo ""

# Check if executables exist, build if needed
if [ ! -f "dist/ZapGazeAgent" ] && [ ! -f "dist/ZapGazeAgent.zip" ]; then
    echo "❌ Executables not found. Building first..."
    ./agent/build.sh
fi

echo "Files ready for release:"
if [ -f "dist/ZapGazeAgent.exe" ]; then
    echo "  ✅ Windows: dist/ZapGazeAgent.exe ($(ls -lh dist/ZapGazeAgent.exe | awk '{print $5}'))"
fi
if [ -f "dist/ZapGazeAgent.zip" ]; then
    echo "  ✅ macOS: dist/ZapGazeAgent.zip ($(ls -lh dist/ZapGazeAgent.zip | awk '{print $5}'))"
fi
if [ -f "dist/ZapGazeAgent" ] && [ ! -f "dist/ZapGazeAgent.zip" ]; then
    echo "  ✅ Linux: dist/ZapGazeAgent ($(ls -lh dist/ZapGazeAgent | awk '{print $5}'))"
fi
echo ""

# Generate release notes
RELEASE_NOTES="## ZapGaze Agent $VERSION

### 🔒 What's New - Security & Authentication

- ✅ **API Key Authentication** - Agent uses embedded API key for secure backend communication
- ✅ **Rate Limiting** - All endpoints protected against abuse with request rate limits
- ✅ **Frontend API Key Support** - Frontend requests now authenticated with API keys
- ✅ **Automatic Authentication** - API key embedded in executable, no user configuration needed

### 🐛 Bug Fixes

- ✅ **Fixed calibration endpoint authentication** - Calibration points now save correctly
- ✅ **Fixed results page** - Session features now load properly
- ✅ **Fixed API key handling** - Agent correctly sends API key in all requests

### Installation

**macOS:**
1. Download \`ZapGazeAgent.zip\`
2. Unzip the file
3. Make executable: \`chmod +x ZapGazeAgent\`
4. Run: \`./ZapGazeAgent\`

**Note:** On first run, macOS may show a security warning. To allow:
- Right-click the file and select \"Open\"
- Click \"Open\" in the security dialog
- Or go to System Preferences > Security & Privacy > General and click \"Open Anyway\"

**Windows:**
1. Download \`ZapGazeAgent.exe\`
2. Double-click to run

**Linux:**
1. Download \`ZapGazeAgent\`
2. Make executable: \`chmod +x ZapGazeAgent\`
3. Run: \`./ZapGazeAgent\`

### Configuration

The agent will connect to the backend at: \`http://20.74.82.26:8000\`

**No API key configuration needed!** The API key is embedded in the executable for secure, automatic authentication.

To change the backend URL, set the \`BACKEND_URL\` environment variable before running:
\`\`\`bash
export BACKEND_URL=http://your-backend-url:8000
./ZapGazeAgent
\`\`\`

### Technical Details

**Security Improvements:**
- API Key Authentication: Agent API key embedded at build time, backend validates all requests
- Rate Limiting: 10-1000 requests/minute per IP depending on endpoint
- Frontend API Key: All frontend endpoints now require authentication
- Calibration endpoints accept both agent and frontend API keys

**Bug Fixes:**
- Fixed calibration endpoint authentication (401 errors resolved)
- Fixed results page feature loading (404 errors resolved)
- Fixed API key header in agent requests
- Improved session features database query reliability

**Breaking Changes:** None - All changes are backward compatible.

### Support

For issues or questions, please open an issue on [GitHub](https://github.com/$REPO/issues)."

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
if [ -f "dist/ZapGazeAgent.zip" ]; then
    echo "   - dist/ZapGazeAgent.zip"
fi
if [ -f "dist/ZapGazeAgent" ] && [ ! -f "dist/ZapGazeAgent.zip" ]; then
    echo "   - dist/ZapGazeAgent (rename to ZapGazeAgent-linux if needed)"
fi
echo "6. Publish release"
echo ""
echo "Download URLs after publishing:"
if [ -f "dist/ZapGazeAgent.exe" ]; then
    echo "  Windows: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent.exe"
fi
if [ -f "dist/ZapGazeAgent.zip" ]; then
    echo "  macOS: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent.zip"
fi
if [ -f "dist/ZapGazeAgent" ] && [ ! -f "dist/ZapGazeAgent.zip" ]; then
    echo "  Linux: https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent"
fi
echo ""

