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
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import styles from "./AgentInstallModal.module.css";

interface AgentInstallModalProps {
  open: boolean;
  onClose: () => void;
  agentUrl: string;
  apiBaseUrl?: string;
  onAgentReady?: () => void;
}

const AgentInstallModal: FC<AgentInstallModalProps> = ({
  open,
  onClose,
  agentUrl,
  apiBaseUrl,
  onAgentReady,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [agentConnected, setAgentConnected] = useState(false);
  type Platform = "windows" | "mac" | "linux" | "unknown";
  const [platform, setPlatform] = useState<Platform>("unknown");
  const [downloadUrls, setDownloadUrls] = useState<Partial<Record<Platform, string>> | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.includes("win")) setPlatform("windows");
    else if (userAgent.includes("mac")) setPlatform("mac");
    else if (userAgent.includes("linux")) setPlatform("linux");

    if (activeStep >= 2 && apiBaseUrl) {
      const interval = setInterval(async () => {
        try {
          const apiKey = import.meta.env?.VITE_FRONTEND_API_KEY;
          const headers: HeadersInit = {};
          if (apiKey) {
            headers["X-API-Key"] = apiKey;
          }

          const response = await fetch(`${apiBaseUrl}/agent/status`, {
            headers,
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
          console.error("Error checking agent status: ", error);
        }
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [activeStep, agentUrl, apiBaseUrl, onAgentReady]);

  useEffect(() => {
    if (!open) return;
    let isMounted = true;

    const fetchLatestRelease = async () => {
      try {
        const response = await fetch(
          "https://api.github.com/repos/Joumanasalahedin/zapgaze/releases/latest"
        );
        if (!response.ok) {
          throw new Error("Failed to fetch latest release");
        }
        const data = await response.json();
        const assets = data?.assets || [];
        const buildUrlMap = (name: string) =>
          assets.find((asset: { name?: string }) => asset.name === name)?.browser_download_url;

        const latestUrls: Partial<Record<Platform, string>> = {
          windows: buildUrlMap("ZapGazeAgent.exe"),
          mac: buildUrlMap("ZapGazeAgent.zip"),
          linux: buildUrlMap("ZapGazeAgent-linux"),
        };

        if (isMounted) {
          const missingPlatforms: Platform[] = [];
          if (!latestUrls.windows) missingPlatforms.push("windows");
          if (!latestUrls.mac) missingPlatforms.push("mac");
          if (!latestUrls.linux) missingPlatforms.push("linux");

          setDownloadUrls(latestUrls);
          setDownloadError(
            missingPlatforms.length
              ? `Latest release is missing assets for: ${missingPlatforms.join(", ")}`
              : null
          );
        }
      } catch (error) {
        console.error("Error fetching latest release: ", error);
        if (isMounted) {
          setDownloadError("Failed to load the latest release. Please try again later.");
        }
      }
    };

    fetchLatestRelease();

    return () => {
      isMounted = false;
    };
  }, [open]);

  const getDownloadUrl = (targetPlatform: Platform = platform): string | null => {
    return downloadUrls?.[targetPlatform] || null;
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

  const handleDownload = (targetPlatform: typeof platform = platform) => {
    const url = getDownloadUrl(targetPlatform);
    if (!url) {
      setDownloadError("Latest download URL is unavailable. Please try again later.");
      return;
    }
    window.open(url, "_blank");
    setActiveStep(1);
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
        <Typography variant="body2" className={styles.mb3}>
          The ZapGaze Agent is required to access your camera for eye-tracking. Follow these steps
          to install and run it:
        </Typography>

        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Download Agent</StepLabel>
            <StepContent>
              <Typography variant="body2" className={styles.mb2}>
                Download the agent for {platform === "unknown" ? "your platform" : platform}:
              </Typography>
              {platform === "unknown" ? (
                <Box className={styles.flexColumnGap1}>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload("windows")}
                  >
                    Windows (.exe)
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload("mac")}
                  >
                    macOS
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={() => handleDownload("linux")}
                  >
                    Linux
                  </Button>
                </Box>
              ) : (
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleDownload()}
                >
                  Download for {platform}
                </Button>
              )}
              {downloadError && (
                <Alert severity="error" className={styles.mt2}>
                  <Typography variant="body2">{downloadError}</Typography>
                </Alert>
              )}
            </StepContent>
          </Step>

          <Step>
            <StepLabel>Run the Agent</StepLabel>
            <StepContent>
              <Typography variant="body2" className={styles.mb2}>
                After downloading:
              </Typography>
              <Box component="ul" className={styles.pl2}>
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
                      <Typography variant="body2" className={styles.mb2}>
                        <strong>Step 1:</strong> Unzip the downloaded file
                      </Typography>
                      <Box component="ol" className={styles.stepListWrapper}>
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
                      <Typography
                        variant="body2"
                        className={`${styles.mb1} ${styles.fontWeightBold}`}
                      >
                        <strong>Step 2:</strong> Run the app
                      </Typography>
                      <Alert severity="warning" className={styles.mb2}>
                        <Typography variant="body2" className={styles.mb1}>
                          <strong>macOS Security Warning:</strong> You'll see a warning saying
                          "ZapGazeAgent" cannot be verified. This is normal for unsigned apps.
                        </Typography>
                      </Alert>
                      <Box component="ol" className={styles.stepListWrapper}>
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
                      <Alert severity="info" className={styles.mt2}>
                        <Typography variant="body2" className={styles.fontSize0875}>
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
              <Button variant="outlined" onClick={() => setActiveStep(2)} className={styles.mt2}>
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
                  <Typography variant="body2" className={styles.mb2}>
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
          <Alert severity="success" className={styles.mt3}>
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
