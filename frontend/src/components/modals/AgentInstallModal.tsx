import { FC, useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Alert,
  Link,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

interface AgentInstallModalProps {
  open: boolean;
  onClose: () => void;
  agentUrl: string; // Deprecated - kept for backward compatibility
  apiBaseUrl?: string; // Backend API URL to check agent status
  onAgentReady?: () => void;
}

const steps = [
  {
    label: "Download",
    description: "Download the ZapGaze Agent for your operating system",
  },
  {
    label: "Run",
    description: "Double-click the downloaded file to start the agent",
  },
  {
    label: "Verify",
    description: "Wait for the connection to be established",
  },
];

const AgentInstallModal: FC<AgentInstallModalProps> = ({
  open,
  onClose,
  agentUrl, // Deprecated
  apiBaseUrl,
  onAgentReady,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [agentConnected, setAgentConnected] = useState(false);
  const [platform, setPlatform] = useState<"windows" | "mac" | "linux" | "unknown">("unknown");

  useEffect(() => {
    // Detect platform
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes("win")) setPlatform("windows");
    else if (userAgent.includes("mac")) setPlatform("mac");
    else if (userAgent.includes("linux")) setPlatform("linux");

    // Check agent status periodically through backend
    if (activeStep >= 2 && apiBaseUrl) {
      const interval = setInterval(async () => {
        try {
          const response = await fetch(`${apiBaseUrl}/agent/status`, {
            signal: AbortSignal.timeout(2000),
          });
          if (response.ok) {
            const data = await response.json();
            if (data.status === "connected") {
              setAgentConnected(true);
              setActiveStep(3);
              if (onAgentReady) {
                onAgentReady();
              }
              clearInterval(interval);
            }
          }
        } catch (error) {
          // Agent not ready yet
        }
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [activeStep, agentUrl, apiBaseUrl, onAgentReady]);

  const getDownloadUrl = (): string => {
    // GitHub Releases URL - Direct link to your release
    // Update this URL after you create the GitHub release
    const baseUrl = "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.3";

    switch (platform) {
      case "windows":
        return `${baseUrl}/ZapGazeAgent.exe`;
      case "mac":
        return `${baseUrl}/ZapGazeAgent.zip`; // macOS app bundle (opens Terminal automatically)
      case "linux":
        return `${baseUrl}/ZapGazeAgent-linux`;
      default:
        return `${baseUrl}/ZapGazeAgent.zip`;
    }
  };

  const getFileName = (): string => {
    switch (platform) {
      case "windows":
        return "ZapGazeAgent.exe";
      case "mac":
        return "ZapGazeAgent.zip";
      case "linux":
        return "ZapGazeAgent";
      default:
        return "ZapGazeAgent.zip";
    }
  };

  const handleDownload = () => {
    const url = getDownloadUrl();
    window.open(url, "_blank");
    setActiveStep(1);
  };

  const handleNext = () => {
    if (activeStep === 0) {
      handleDownload();
    } else {
      setActiveStep((prev) => prev + 1);
    }
  };

  const handleClose = () => {
    if (agentConnected) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Install ZapGaze Agent</DialogTitle>
      <DialogContent>
        <Typography variant="body2" sx={{ mb: 3 }}>
          The ZapGaze Agent is required to access your camera for eye-tracking. Follow these steps
          to install and run it:
        </Typography>

        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Download Agent</StepLabel>
            <StepContent>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Download the agent for {platform === "unknown" ? "your platform" : platform}:
              </Typography>
              {platform === "unknown" ? (
                <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => {
                      const baseUrl =
                        "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.3";
                      window.open(`${baseUrl}/ZapGazeAgent.exe`, "_blank");
                      setActiveStep(1);
                    }}
                  >
                    Windows (.exe)
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => {
                      const baseUrl =
                        "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.3";
                      window.open(`${baseUrl}/ZapGazeAgent.zip`, "_blank");
                      setActiveStep(1);
                    }}
                  >
                    macOS
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => {
                      const baseUrl =
                        "https://github.com/Joumanasalahedin/zapgaze/releases/download/v1.0.3";
                      window.open(`${baseUrl}/ZapGazeAgent-linux`, "_blank");
                      setActiveStep(1);
                    }}
                  >
                    Linux
                  </Button>
                </Box>
              ) : (
                <Button variant="contained" startIcon={<DownloadIcon />} onClick={handleDownload}>
                  Download for {platform}
                </Button>
              )}
            </StepContent>
          </Step>

          <Step>
            <StepLabel>Run the Agent</StepLabel>
            <StepContent>
              <Typography variant="body2" sx={{ mb: 2 }}>
                After downloading:
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                <li>
                  <Typography variant="body2">
                    Locate the downloaded file: <strong>{getFileName()}</strong>
                  </Typography>
                </li>
                <li>
                  {platform === "windows" ? (
                    <Typography variant="body2">Double-click the .exe file to run it</Typography>
                  ) : platform === "mac" ? (
                    <Box>
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        <strong>Step 1:</strong> Unzip the downloaded file
                      </Typography>
                      <Box component="ol" sx={{ marginTop: 1, paddingLeft: 3, mb: 2 }}>
                        <li>
                          <Typography variant="body2">
                            Double-click <strong>ZapGazeAgent.zip</strong> to unzip it
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            This will create <strong>ZapGazeAgent.app</strong> in your Downloads
                            folder
                          </Typography>
                        </li>
                      </Box>
                      <Typography variant="body2" sx={{ mb: 1, fontWeight: "bold" }}>
                        <strong>Step 2:</strong> Run the app
                      </Typography>
                      <Alert severity="warning" sx={{ mb: 2 }}>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>macOS Security Warning:</strong> You'll see a warning saying
                          "ZapGazeAgent" cannot be verified. This is normal for unsigned apps.
                        </Typography>
                      </Alert>
                      <Box component="ol" sx={{ marginTop: 1, paddingLeft: 3, mb: 2 }}>
                        <li>
                          <Typography variant="body2">
                            Right-click (or Control+click) on <strong>ZapGazeAgent.app</strong>
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            Select <strong>"Open"</strong> from the context menu
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            In the security dialog, click <strong>"Open"</strong>
                          </Typography>
                        </li>
                        <li>
                          <Typography variant="body2">
                            A Terminal window will open automatically with the agent running
                          </Typography>
                        </li>
                      </Box>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontSize: "0.875rem" }}>
                          <strong>Note:</strong> The app bundle preserves execute permissions and
                          automatically opens Terminal. After the first time, you can double-click
                          ZapGazeAgent.app directly.
                        </Typography>
                      </Alert>
                    </Box>
                  ) : (
                    <Typography variant="body2">
                      Make it executable: chmod +x ZapGazeAgent, then run: ./ZapGazeAgent
                    </Typography>
                  )}
                </li>
                <li>
                  <Typography variant="body2">
                    A terminal window will open showing the agent status
                  </Typography>
                </li>
              </Box>
              <Button variant="outlined" onClick={() => setActiveStep(2)} sx={{ mt: 2 }}>
                I've started the agent
              </Button>
            </StepContent>
          </Step>

          <Step>
            <StepLabel>Verify Connection</StepLabel>
            <StepContent>
              {agentConnected ? (
                <Alert severity="success" icon={<CheckCircleIcon />}>
                  <Typography variant="body2">
                    Agent connected successfully! You can now proceed with the test.
                  </Typography>
                </Alert>
              ) : (
                <Box>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    Waiting for agent to connect...
                  </Typography>
                  <Alert severity="info">
                    <Typography variant="body2">
                      Make sure the agent is running and not blocked by your firewall.
                    </Typography>
                  </Alert>
                </Box>
              )}
            </StepContent>
          </Step>
        </Stepper>

        {agentConnected && (
          <Alert severity="success" sx={{ mt: 3 }}>
            <Typography variant="body2">
              Setup complete! The agent is now connected and ready to use.
            </Typography>
          </Alert>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={!agentConnected}>
          {agentConnected ? "Continue" : "Close"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AgentInstallModal;
