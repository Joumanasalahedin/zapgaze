#!/usr/bin/env bash
# Script to help create GitHub releases for ZapGaze Agent
# Usage: ./scripts/create-release.sh v1.0.0

set -e

VERSION=${1:-v1.0.0}
REPO="Joumanasalahedin/zapgaze"

echo "=========================================="
echo "Creating GitHub Release: $VERSION"
echo "=========================================="
echo ""

# Check if executable exists
if [ ! -f "dist/ZapGazeAgent" ]; then
    echo "❌ Executable not found. Building first..."
    ./agent/build.sh
fi

echo "✅ Executable found: dist/ZapGazeAgent"
echo "   Size: $(ls -lh dist/ZapGazeAgent | awk '{print $5}')"
echo ""

echo "Next steps:"
echo "1. Go to: https://github.com/$REPO/releases/new"
echo "2. Tag version: $VERSION"
echo "3. Title: ZapGaze Agent $VERSION"
echo "4. Upload file: dist/ZapGazeAgent"
echo "5. Publish release"
echo ""
echo "After publishing, the download URL will be:"
echo "https://github.com/$REPO/releases/download/$VERSION/ZapGazeAgent"
echo ""

