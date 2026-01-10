# CDN Explanation for Hosting Executables

## What is a CDN?

**CDN** stands for **Content Delivery Network**. Think of it as a network of servers around the world that store and deliver files (like images, videos, software downloads) to users.

### Simple Analogy

Imagine you have a book (your executable file):
- **Without CDN**: Everyone has to come to your house (your server) to get the book
- **With CDN**: Copies of your book are stored in libraries (CDN servers) all over the world, so people can get it from the nearest library

### Why Use a CDN?

1. **Fast Downloads**: Files are served from servers close to users
2. **Reliability**: If one server goes down, others can still serve the file
3. **Scalability**: Can handle many downloads without overloading your main server
4. **Cost-Effective**: Usually cheaper than serving large files from your main server

## Options for Hosting Your Executables

You don't necessarily need a traditional CDN. Here are your options:

### Option 1: AWS S3 + CloudFront (Recommended)

**What it is:**
- **S3**: Amazon's storage service (like a hard drive in the cloud)
- **CloudFront**: Amazon's CDN (distributes files globally)

**How it works:**
1. Upload your executables to S3 (storage)
2. CloudFront automatically distributes them to edge locations worldwide
3. Users download from the nearest location

**Cost:** ~$0.023 per GB stored + ~$0.085 per GB downloaded

**Example:**
```
Your executable: 150MB
1000 downloads = 150GB
Cost: ~$12.75 for storage + downloads
```

**Setup:**
```bash
# 1. Create S3 bucket
aws s3 mb s3://zapgaze-agent-downloads

# 2. Upload executables
aws s3 cp dist/ZapGazeAgent.exe s3://zapgaze-agent-downloads/
aws s3 cp dist/ZapGazeAgent s3://zapgaze-agent-downloads/ZapGazeAgent-mac

# 3. Make files publicly accessible
aws s3api put-object-acl \
  --bucket zapgaze-agent-downloads \
  --key ZapGazeAgent.exe \
  --acl public-read

# 4. Get the URL
# URL will be: https://zapgaze-agent-downloads.s3.amazonaws.com/ZapGazeAgent.exe
```

### Option 2: Azure Blob Storage + CDN

**What it is:**
- **Blob Storage**: Azure's file storage service
- **Azure CDN**: Azure's content delivery network

**How it works:**
Similar to AWS - store files in Blob Storage, serve via CDN

**Cost:** ~$0.0184 per GB stored + ~$0.081 per GB downloaded

**Setup:**
```bash
# 1. Create storage account
az storage account create --name zapgazeagent --resource-group zapgaze-rg

# 2. Create container
az storage container create \
  --name downloads \
  --account-name zapgazeagent \
  --public-access blob

# 3. Upload files
az storage blob upload \
  --account-name zapgazeagent \
  --container-name downloads \
  --name ZapGazeAgent.exe \
  --file dist/ZapGazeAgent.exe

# 4. Get URL
# URL: https://zapgazeagent.blob.core.windows.net/downloads/ZapGazeAgent.exe
```

### Option 3: GitHub Releases (Free & Simple)

**What it is:**
- GitHub's built-in file hosting for releases
- Free for public repositories

**How it works:**
1. Create a GitHub release
2. Upload executables as release assets
3. GitHub hosts them and provides download links

**Cost:** FREE (for public repos)

**Setup:**
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version (e.g., `v1.0.0`)
4. Upload `ZapGazeAgent.exe`, `ZapGazeAgent-mac`, `ZapGazeAgent-linux`
5. Get download URLs:
   ```
   https://github.com/yourusername/zapgaze/releases/download/v1.0.0/ZapGazeAgent.exe
   ```

**Pros:**
- ✅ Free
- ✅ Simple
- ✅ Version management built-in
- ✅ No setup required

**Cons:**
- ❌ Not a true CDN (slower for some users)
- ❌ Public repos only (private repos have limits)

### Option 4: Your Own Web Server

**What it is:**
- Serve files from your existing web server

**How it works:**
1. Upload executables to your server (e.g., `/var/www/downloads/`)
2. Serve them via HTTP/HTTPS
3. Users download directly from your server

**Example:**
```
https://yourdomain.com/downloads/ZapGazeAgent.exe
```

**Pros:**
- ✅ Full control
- ✅ No extra service needed

**Cons:**
- ❌ Slower for distant users
- ❌ Uses your server bandwidth
- ❌ Can overload your server with many downloads

### Option 5: Cloudflare R2 (New, Cheaper Alternative)

**What it is:**
- Cloudflare's S3-compatible storage
- No egress fees (free downloads!)

**Cost:** ~$0.015 per GB stored, $0 downloads

**Best for:** High download volume

## Recommended Approach for Your Project

### For MVP/Testing: GitHub Releases
- **Why:** Free, simple, no setup
- **URL Pattern:** `https://github.com/yourusername/zapgaze/releases/download/v1.0.0/ZapGazeAgent.exe`

### For Production: AWS S3 + CloudFront or Azure Blob + CDN
- **Why:** Fast, reliable, scalable
- **URL Pattern:** `https://cdn.yourdomain.com/zapgaze-agent/v1.0.0/ZapGazeAgent.exe`

## How to Configure in Your Frontend

### Option A: GitHub Releases

```typescript
// In AgentStatusChecker.tsx
const getDownloadUrl = (platform: string): string => {
    const version = 'v1.0.0'; // Update this when you release new versions
    const baseUrl = `https://github.com/yourusername/zapgaze/releases/download/${version}`;
    
    switch (platform) {
        case 'windows':
            return `${baseUrl}/ZapGazeAgent.exe`;
        case 'mac':
            return `${baseUrl}/ZapGazeAgent-mac`;
        case 'linux':
            return `${baseUrl}/ZapGazeAgent-linux`;
        default:
            return baseUrl;
    }
};
```

### Option B: AWS S3

```typescript
const getDownloadUrl = (platform: string): string => {
    const baseUrl = 'https://zapgaze-agent-downloads.s3.amazonaws.com';
    // or with CloudFront: 'https://d1234567890.cloudfront.net'
    
    switch (platform) {
        case 'windows':
            return `${baseUrl}/ZapGazeAgent.exe`;
        // ... etc
    }
};
```

### Option C: Environment Variable (Best Practice)

```bash
# In your deployment
VITE_AGENT_DOWNLOAD_URL=https://github.com/yourusername/zapgaze/releases/download/v1.0.0
```

Then in code:
```typescript
const baseUrl = process.env.VITE_AGENT_DOWNLOAD_URL || 'https://your-cdn.com/zapgaze-agent';
```

## Step-by-Step: GitHub Releases (Easiest)

1. **Build your executables:**
   ```bash
   ./agent/build.sh
   ```

2. **Create a GitHub release:**
   - Go to your GitHub repo
   - Click "Releases" → "Create a new release"
   - Tag: `v1.0.0`
   - Title: "ZapGaze Agent v1.0.0"
   - Upload files:
     - `dist/ZapGazeAgent.exe` (rename to `ZapGazeAgent.exe`)
     - `dist/ZapGazeAgent` (rename to `ZapGazeAgent-mac`)
     - `dist/ZapGazeAgent` (rename to `ZapGazeAgent-linux`)

3. **Get the download URLs:**
   - Right-click each file → "Copy link address"
   - URLs will look like:
     ```
     https://github.com/yourusername/zapgaze/releases/download/v1.0.0/ZapGazeAgent.exe
     ```

4. **Update your frontend:**
   ```typescript
   const baseUrl = 'https://github.com/yourusername/zapgaze/releases/download/v1.0.0';
   ```

## Summary

- **CDN** = Network of servers that deliver files quickly to users worldwide
- **You need it** to host your executable files so users can download them
- **Easiest option**: GitHub Releases (free, simple)
- **Production option**: AWS S3 + CloudFront or Azure Blob + CDN (faster, more reliable)
- **Your frontend** will use these URLs to provide download links to users

The key is: **You need somewhere to put your executable files on the internet** so users can download them. A CDN makes those downloads fast and reliable.

