# Agent Download Setup Guide

## Overview

The frontend now includes components to detect and help users install the ZapGaze Agent. You need to:

1. **Host the executables** somewhere accessible (CDN, S3, etc.)
2. **Configure the download URLs** in the frontend

## Frontend Components Created

1. **`AgentStatusChecker`** - Checks if agent is running, shows download button if not
2. **`AgentInstallModal`** - Step-by-step installation guide with platform detection
3. **Integrated into `TestPage`** - Automatically checks agent status and blocks test start if not connected

## Setup Steps

### Step 1: Host the Executables

You need to host the built executables somewhere users can download them:

**Option A: AWS S3 + CloudFront**
```bash
# Upload executables to S3
aws s3 cp dist/ZapGazeAgent.exe s3://your-bucket/zapgaze-agent/ZapGazeAgent.exe
aws s3 cp dist/ZapGazeAgent s3://your-bucket/zapgaze-agent/ZapGazeAgent-mac
aws s3 cp dist/ZapGazeAgent s3://your-bucket/zapgaze-agent/ZapGazeAgent-linux

# Make them publicly accessible
aws s3api put-object-acl --bucket your-bucket --key zapgaze-agent/ZapGazeAgent.exe --acl public-read
```

**Option B: Azure Blob Storage**
```bash
az storage blob upload \
  --account-name yourstorage \
  --container-name downloads \
  --name ZapGazeAgent.exe \
  --file dist/ZapGazeAgent.exe \
  --public-access blob
```

**Option C: GitHub Releases**
- Create a GitHub release
- Upload executables as release assets
- Use GitHub's CDN URLs

**Option D: Your Own Server/CDN**
- Upload to your web server
- Serve from `/downloads/` or similar path

### Step 2: Configure Download URLs

Set the environment variable in your frontend build:

**For local development:**
Create `frontend/.env.local`:
```env
VITE_AGENT_DOWNLOAD_URL=https://your-cdn.com/zapgaze-agent
```

**For production (Azure/AWS):**
Set environment variable during build:
```bash
VITE_AGENT_DOWNLOAD_URL=https://your-cdn.com/zapgaze-agent npm run build
```

Or in your deployment configuration:
- **Azure Static Web Apps**: Add to `azure-static-web-apps.yml`
- **AWS CloudFront**: Set in build script
- **Docker**: Add to `docker-compose.yml` environment variables

### Step 3: File Naming Convention

The frontend expects these file names:
- **Windows**: `ZapGazeAgent.exe`
- **macOS**: `ZapGazeAgent-mac`
- **Linux**: `ZapGazeAgent-linux`

Or use the base URL pattern:
```
https://your-cdn.com/zapgaze-agent/ZapGazeAgent.exe
https://your-cdn.com/zapgaze-agent/ZapGazeAgent-mac
https://your-cdn.com/zapgaze-agent/ZapGazeAgent-linux
```

## How It Works

1. **User visits test page** → Frontend checks `http://localhost:9000/status`
2. **If agent not running** → Shows "Download Agent" button
3. **User clicks download** → Opens download modal with platform detection
4. **User downloads and runs** → Frontend polls for connection
5. **Agent connects** → Test can proceed

## Testing Locally

1. **Without agent running:**
   - Visit test page
   - Should see "Agent not connected" message
   - Click "Download Agent" → Modal opens

2. **With agent running:**
   - Run `./dist/ZapGazeAgent`
   - Visit test page
   - Should see "Agent connected and ready"

## Customization

### Change Download URLs

Edit `AgentStatusChecker.tsx` and `AgentInstallModal.tsx`:
```typescript
const baseUrl = process.env.VITE_AGENT_DOWNLOAD_URL || 'https://your-cdn.com/zapgaze-agent';
```

### Change Status Check Interval

In `AgentStatusChecker.tsx`:
```typescript
const interval = setInterval(checkAgentStatus, 3000); // Change 3000 to desired ms
```

### Customize Modal Content

Edit `AgentInstallModal.tsx` to change:
- Step descriptions
- Platform-specific instructions
- Download button text

## Security Considerations

1. **HTTPS Only**: Always serve executables over HTTPS
2. **Code Signing**: Sign executables to prevent security warnings
3. **Virus Scanning**: Scan executables before hosting
4. **Version Control**: Include version numbers in filenames (e.g., `ZapGazeAgent-v1.0.0.exe`)

## Example Deployment Script

```bash
#!/bin/bash
# deploy-agent-downloads.sh

VERSION="1.0.0"
CDN_URL="https://cdn.yourdomain.com/zapgaze-agent"

# Build executables
./agent/build.sh

# Upload to CDN
aws s3 cp dist/ZapGazeAgent.exe \
  s3://your-bucket/zapgaze-agent/v${VERSION}/ZapGazeAgent.exe \
  --acl public-read

aws s3 cp dist/ZapGazeAgent \
  s3://your-bucket/zapgaze-agent/v${VERSION}/ZapGazeAgent-mac \
  --acl public-read

# Update frontend env
echo "VITE_AGENT_DOWNLOAD_URL=${CDN_URL}/v${VERSION}" > frontend/.env.production

# Rebuild frontend
cd frontend && npm run build
```

## Next Steps

1. ✅ Build executables for all platforms
2. ✅ Set up hosting (S3, Azure Blob, etc.)
3. ✅ Configure `VITE_AGENT_DOWNLOAD_URL` environment variable
4. ✅ Test download flow end-to-end
5. ✅ Deploy frontend with new components

