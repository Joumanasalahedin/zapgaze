import { FC, useState, useEffect } from "react";
import { Button, Box, Typography, Alert, CircularProgress } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";

interface AgentStatusCheckerProps {
  agentUrl: string; // Deprecated - kept for backward compatibility
  apiBaseUrl?: string; // Backend API URL to check agent status
  onAgentReady?: () => void;
  showDownloadButton?: boolean;
}

type AgentStatus = "checking" | "connected" | "disconnected" | "error";

const AgentStatusChecker: FC<AgentStatusCheckerProps> = ({
  agentUrl, // Deprecated
  apiBaseUrl,
  onAgentReady,
  showDownloadButton = true,
}) => {
  const [status, setStatus] = useState<AgentStatus>("checking");
  const [showDownload, setShowDownload] = useState(false);
  const [corsError, setCorsError] = useState(false);

  useEffect(() => {
    checkAgentStatus();
    // Check every 3 seconds
    const interval = setInterval(checkAgentStatus, 3000);
    return () => clearInterval(interval);
  }, [agentUrl, apiBaseUrl]);

  const checkAgentStatus = async () => {
    // Use backend API if provided, otherwise fall back to direct agent URL
    const statusUrl = apiBaseUrl 
      ? `${apiBaseUrl}/agent/status`
      : `${agentUrl}/status`;

    try {
      const response = await fetch(statusUrl, {
        method: "GET",
        // Add timeout
        signal: AbortSignal.timeout(2000),
      });

      if (response.ok) {
        const data = await response.json();
        // Backend returns {status: "connected"} or {status: "disconnected"}
        if (data.status === "connected") {
          setStatus("connected");
          setCorsError(false);
          if (onAgentReady) {
            onAgentReady();
          }
        } else {
          setStatus("disconnected");
          setCorsError(false);
        }
      } else {
        setStatus("disconnected");
        setCorsError(false);
      }
    } catch (error: any) {
      // Check for CORS/Private Network Access error (only for direct agent URL)
      if (!apiBaseUrl) {
        const errorMessage = error?.message || "";
        if (
          errorMessage.includes("CORS") ||
          errorMessage.includes("more-private address space") ||
          errorMessage.includes("loopback")
        ) {
          setCorsError(true);
          setStatus("error");
          return;
        }
      }
      // Network error or timeout - agent not running
      setCorsError(false);
      setStatus("disconnected");
    }
  };

  const getPlatform = (): "windows" | "mac" | "linux" | "unknown" => {
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes("win")) return "windows";
    if (userAgent.includes("mac")) return "mac";
    if (userAgent.includes("linux")) return "linux";
    return "unknown";
  };

  const isLocalDevelopment = () => {
    return window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  };

  const getDownloadUrl = (platform: string): string => {
    // For local development, provide instructions instead of download link
    if (isLocalDevelopment()) {
      return ""; // Will show instructions instead
    }

    // GitHub Releases URL - Direct link to your release
    // Update this URL after you create the GitHub release
    const baseUrl = "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.1";

    switch (platform) {
      case "windows":
        return `${baseUrl}/ZapGazeAgent.exe`;
      case "mac":
        return `${baseUrl}/ZapGazeAgent`; // macOS executable
      case "linux":
        return `${baseUrl}/ZapGazeAgent-linux`; // If you build Linux version later
      default:
        return `${baseUrl}/ZapGazeAgent`;
    }
  };

  const handleDownload = () => {
    const platform = getPlatform();
    const downloadUrl = getDownloadUrl(platform);

    if (platform === "unknown") {
      // Show all platform options
      setShowDownload(true);
      return;
    }

    // For local development, show instructions
    if (isLocalDevelopment()) {
      setShowDownload(true);
      return;
    }

    // Open GitHub release URL - browser will handle the download
    if (downloadUrl) {
      window.open(downloadUrl, "_blank");
    }
  };

  if (status === "checking") {
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <CircularProgress size={20} />
        <Typography variant="body2">Checking agent connection...</Typography>
      </Box>
    );
  }

  if (status === "connected") {
    return (
      <Alert
        severity="success"
        icon={<CheckCircleIcon />}
        sx={{ display: "flex", alignItems: "center" }}
      >
        <Typography variant="body2">Agent connected and ready</Typography>
      </Alert>
    );
  }

  // CORS error - browser blocking localhost access
  if (corsError) {
    return (
      <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1, fontWeight: "bold" }}>
          Browser Security Restriction Detected
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          Your browser is blocking access to the local agent because the app is served from a remote server.
          To fix this, you need to access the app via localhost:
        </Typography>
        <Box component="ol" sx={{ pl: 3, mb: 2 }}>
          <li>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Set up SSH port forwarding from your local machine:
            </Typography>
            <Box
              component="pre"
              sx={{
                bgcolor: "grey.100",
                p: 1,
                borderRadius: 1,
                fontSize: "0.875rem",
                overflow: "auto",
                mb: 1,
              }}
            >
              ssh -L 5173:localhost:5173 -L 9000:localhost:9000 azureuser@20.74.82.26
            </Box>
          </li>
          <li>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Then open the app in a new tab at:{" "}
              <strong>http://localhost:5173</strong>
            </Typography>
          </li>
          <li>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Important:</strong> The command above forwards both the frontend (port 5173) 
              and the agent (port 9000) so the app can communicate with your local agent.
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Make sure the ZapGaze Agent is running on your local machine.
            </Typography>
          </li>
        </Box>
        <Typography variant="body2" sx={{ fontSize: "0.875rem", color: "text.secondary" }}>
          This is a browser security feature that prevents remote websites from accessing your localhost.
        </Typography>
      </Alert>
    );
  }

  // Disconnected - show download option
  return (
    <Box>
      <Alert severity="warning" icon={<ErrorIcon />} sx={{ mb: 2 }}>
        <Typography variant="body2" sx={{ mb: 1 }}>
          ZapGaze Agent is not running. Please download and install it to continue.
        </Typography>
        {showDownloadButton && (
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={handleDownload}
            size="small"
          >
            Download Agent
          </Button>
        )}
      </Alert>

      {showDownload && (
        <Box sx={{ mt: 2, p: 2, bgcolor: "background.paper", borderRadius: 1 }}>
          {isLocalDevelopment() ? (
            <>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Local Development Instructions:
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                For local testing, use the executable you built:
              </Typography>
              <Box
                component="pre"
                sx={{
                  bgcolor: "grey.100",
                  p: 1,
                  borderRadius: 1,
                  fontSize: "0.875rem",
                  overflow: "auto",
                }}
              >
                {getPlatform() === "mac" || getPlatform() === "linux"
                  ? "./dist/ZapGazeAgent"
                  : "dist\\ZapGazeAgent.exe"}
              </Box>
              <Typography
                variant="body2"
                sx={{ mt: 2, fontSize: "0.875rem", color: "text.secondary" }}
              >
                Run this command in your terminal from the project root directory.
              </Typography>
            </>
          ) : (
            <>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>
                Download for your platform:
              </Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                <Button
                  variant="outlined"
                  onClick={() => {
                    const url = getDownloadUrl("windows");
                    if (url) window.open(url, "_blank");
                  }}
                >
                  Windows (.exe)
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    const url = getDownloadUrl("mac");
                    if (url) window.open(url, "_blank");
                  }}
                >
                  macOS
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    const url = getDownloadUrl("linux");
                    if (url) window.open(url, "_blank");
                  }}
                >
                  Linux
                </Button>
              </Box>
            </>
          )}
        </Box>
      )}
    </Box>
  );
};

export default AgentStatusChecker;
