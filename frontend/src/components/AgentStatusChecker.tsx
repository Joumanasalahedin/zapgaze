import { FC, useState, useEffect } from 'react';
import { Button, Box, Typography, Alert, CircularProgress } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

interface AgentStatusCheckerProps {
    agentUrl: string;
    onAgentReady?: () => void;
    showDownloadButton?: boolean;
}

type AgentStatus = 'checking' | 'connected' | 'disconnected' | 'error';

const AgentStatusChecker: FC<AgentStatusCheckerProps> = ({
    agentUrl,
    onAgentReady,
    showDownloadButton = true,
}) => {
    const [status, setStatus] = useState<AgentStatus>('checking');
    const [showDownload, setShowDownload] = useState(false);

    useEffect(() => {
        checkAgentStatus();
        // Check every 3 seconds
        const interval = setInterval(checkAgentStatus, 3000);
        return () => clearInterval(interval);
    }, [agentUrl]);

    const checkAgentStatus = async () => {
        try {
            const response = await fetch(`${agentUrl}/status`, {
                method: 'GET',
                // Add timeout
                signal: AbortSignal.timeout(2000),
            });
            
            if (response.ok) {
                const data = await response.json();
                setStatus('connected');
                if (onAgentReady) {
                    onAgentReady();
                }
            } else {
                setStatus('disconnected');
            }
        } catch (error) {
            // Network error or timeout - agent not running
            setStatus('disconnected');
        }
    };

    const getPlatform = (): 'windows' | 'mac' | 'linux' | 'unknown' => {
        const userAgent = navigator.userAgent.toLowerCase();
        if (userAgent.includes('win')) return 'windows';
        if (userAgent.includes('mac')) return 'mac';
        if (userAgent.includes('linux')) return 'linux';
        return 'unknown';
    };

    const isLocalDevelopment = () => {
        return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    };

    const getDownloadUrl = (platform: string): string => {
        // For local development, provide instructions instead of download link
        if (isLocalDevelopment()) {
            return ''; // Will show instructions instead
        }
        
        // These URLs will need to be configured based on where you host the executables
        const baseUrl = process.env.VITE_AGENT_DOWNLOAD_URL || 'https://your-cdn.com/zapgaze-agent';
        
        switch (platform) {
            case 'windows':
                return `${baseUrl}/ZapGazeAgent.exe`;
            case 'mac':
                return `${baseUrl}/ZapGazeAgent-mac`;
            case 'linux':
                return `${baseUrl}/ZapGazeAgent-linux`;
            default:
                return `${baseUrl}`;
        }
    };

    const handleDownload = () => {
        const platform = getPlatform();
        const downloadUrl = getDownloadUrl(platform);
        
        if (platform === 'unknown') {
            // Show all platform options
            setShowDownload(true);
            return;
        }

        // For local development, show instructions
        if (isLocalDevelopment()) {
            setShowDownload(true);
            return;
        }

        // Trigger download
        if (downloadUrl) {
            window.open(downloadUrl, '_blank');
        }
    };

    if (status === 'checking') {
        return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} />
                <Typography variant="body2">Checking agent connection...</Typography>
            </Box>
        );
    }

    if (status === 'connected') {
        return (
            <Alert 
                severity="success" 
                icon={<CheckCircleIcon />}
                sx={{ display: 'flex', alignItems: 'center' }}
            >
                <Typography variant="body2">
                    Agent connected and ready
                </Typography>
            </Alert>
        );
    }

    // Disconnected - show download option
    return (
        <Box>
            <Alert 
                severity="warning" 
                icon={<ErrorIcon />}
                sx={{ mb: 2 }}
            >
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
                <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                    {isLocalDevelopment() ? (
                        <>
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                Local Development Instructions:
                            </Typography>
                            <Typography variant="body2" sx={{ mb: 2 }}>
                                For local testing, use the executable you built:
                            </Typography>
                            <Box component="pre" sx={{ 
                                bgcolor: 'grey.100', 
                                p: 1, 
                                borderRadius: 1,
                                fontSize: '0.875rem',
                                overflow: 'auto'
                            }}>
                                {getPlatform() === 'mac' || getPlatform() === 'linux' 
                                    ? './dist/ZapGazeAgent'
                                    : 'dist\\ZapGazeAgent.exe'
                                }
                            </Box>
                            <Typography variant="body2" sx={{ mt: 2, fontSize: '0.875rem', color: 'text.secondary' }}>
                                Run this command in your terminal from the project root directory.
                            </Typography>
                        </>
                    ) : (
                        <>
                            <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                Download for your platform:
                            </Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <Button
                                    variant="outlined"
                                    onClick={() => {
                                        const url = getDownloadUrl('windows');
                                        if (url) window.open(url, '_blank');
                                    }}
                                >
                                    Windows (.exe)
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => {
                                        const url = getDownloadUrl('mac');
                                        if (url) window.open(url, '_blank');
                                    }}
                                >
                                    macOS
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={() => {
                                        const url = getDownloadUrl('linux');
                                        if (url) window.open(url, '_blank');
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

