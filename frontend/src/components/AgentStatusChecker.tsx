import { FC, useState, useEffect } from "react";
import { Button, Box, Typography, Alert, CircularProgress } from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";

interface AgentStatusCheckerProps {
  agentUrl: string;
  apiBaseUrl?: string;
  onAgentReady?: () => void;
  showDownloadButton?: boolean;
}

type AgentStatus = "checking" | "connected" | "disconnected" | "error";

const AgentStatusChecker: FC<AgentStatusCheckerProps> = ({
  agentUrl,
  apiBaseUrl,
  onAgentReady,
  showDownloadButton = true,
}) => {
  const [status, setStatus] = useState<AgentStatus>("checking");
  const [showDownload, setShowDownload] = useState(false);
  const [waitingForAgent, setWaitingForAgent] = useState(false);

  useEffect(() => {
    checkAgentStatus();
    const interval = setInterval(checkAgentStatus, 3000);
    return () => clearInterval(interval);
  }, [agentUrl, apiBaseUrl]);

  const checkAgentStatus = async () => {
    const statusUrl = apiBaseUrl ? `${apiBaseUrl}/agent/status` : `${agentUrl}/status`;
    const apiKey = import.meta.env?.VITE_FRONTEND_API_KEY;

    try {
      const headers: HeadersInit = {};
      if (apiBaseUrl && apiKey) {
        headers["X-API-Key"] = apiKey;
      }

      const response = await fetch(statusUrl, {
        method: "GET",
        headers,
        signal: AbortSignal.timeout(2000),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === "connected") {
          setStatus("connected");
          setWaitingForAgent(false);
          if (onAgentReady) {
            onAgentReady();
          }
        } else {
          setStatus("disconnected");
        }
      } else {
        setStatus("disconnected");
      }
    } catch (error: any) {
      if (!apiBaseUrl) {
        const errorMessage = error?.message || "";
        if (
          errorMessage.includes("CORS") ||
          errorMessage.includes("more-private address space") ||
          errorMessage.includes("loopback")
        ) {
          setStatus("error");
          return;
        }
      }
      setStatus("disconnected");
    }
  };

  const getPlatform = (): "windows" | "mac" | "unknown" => {
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes("win")) return "windows";
    if (userAgent.includes("mac")) return "mac";
    return "unknown";
  };

  const getDownloadUrl = (platform: string): string => {
    const baseUrl = "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.4";

    switch (platform) {
      case "windows":
        return `${baseUrl}/ZapGazeAgent.exe`;
      case "mac":
        return `${baseUrl}/ZapGazeAgent.zip`;
      default:
        return `${baseUrl}/ZapGazeAgent.zip`;
    }
  };

  const handleDownload = () => {
    const platform = getPlatform();

    if (platform === "unknown") {
      setShowDownload(true);
      return;
    }

    setShowDownload(true);
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

  if (waitingForAgent) {
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <CircularProgress size={20} />
        <Typography variant="body2">Waiting for agent to connect...</Typography>
      </Box>
    );
  }

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
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Download for your platform:
          </Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
            <Button
              variant="outlined"
              onClick={() => {
                const url = getDownloadUrl("windows");
                if (url) {
                  window.open(url, "_blank");
                  setWaitingForAgent(true);
                  setShowDownload(false);
                }
              }}
            >
              Windows (.exe)
            </Button>
            <Button
              variant="outlined"
              onClick={() => {
                const url = getDownloadUrl("mac");
                if (url) {
                  window.open(url, "_blank");
                  setWaitingForAgent(true);
                  setShowDownload(false);
                }
              }}
            >
              macOS
            </Button>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default AgentStatusChecker;
