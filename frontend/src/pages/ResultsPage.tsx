import { FC, useState } from "react";
import { useNavigate } from "react-router-dom";
import Paper from "@mui/material/Paper";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import CircularProgress from "@mui/material/CircularProgress";
import Alert from "@mui/material/Alert";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

interface SessionResult {
  session_uid: string;
  started_at: string | null;
  stopped_at: string | null;
  status: string;
  features: any;
  intake: any;
}

interface UserResults {
  user_id: number;
  user_name: string;
  birthdate: string;
  sessions: SessionResult[];
}

const ResultsPage: FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [birthdate, setBirthdate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<UserResults | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const apiKey = import.meta.env.VITE_FRONTEND_API_KEY;
      const apiUrl = import.meta.env.VITE_API_URL || "http://20.74.82.26:8000";

      const response = await fetch(
        `${apiUrl}/users/results/by-credentials?name=${encodeURIComponent(name)}&birthdate=${birthdate}`,
        {
          headers: {
            ...(apiKey ? { "X-API-Key": apiKey } : {}),
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(errorData.detail || "Failed to fetch results");
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Failed to load results. Please check your name and birthdate.");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={{ margin: "3.2rem auto", padding: "32px 24px 24px 24px", maxWidth: "1200px" }}>
      <h1>View Your Results</h1>
      <p style={{ marginBottom: "24px", color: "#666" }}>
        Enter your name and birthdate (as used in the intake form) to view your previous test
        results.
      </p>

      <Paper elevation={2} style={{ padding: "24px", marginBottom: "24px" }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "flex-end" }}>
            <TextField
              label="Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              fullWidth
              sx={{ flex: "1 1 300px" }}
              placeholder="Enter your name"
            />
            <TextField
              label="Birthdate"
              type="date"
              value={birthdate}
              onChange={(e) => setBirthdate(e.target.value)}
              required
              InputLabelProps={{ shrink: true }}
              sx={{ flex: "1 1 200px" }}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !name.trim() || !birthdate}
              sx={{ minWidth: "120px" }}
            >
              {loading ? <CircularProgress size={20} /> : "Search"}
            </Button>
          </Box>
        </form>
      </Paper>

      {error && (
        <Alert severity="error" style={{ marginBottom: "24px" }}>
          {error}
        </Alert>
      )}

      {results && (
        <div>
          <Paper
            elevation={2}
            style={{ padding: "20px", marginBottom: "24px", backgroundColor: "#f5f5f5" }}
          >
            <Typography variant="h5" gutterBottom>
              Results for: {results.user_name}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Birthdate: {new Date(results.birthdate).toLocaleDateString("de-DE")}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Total Sessions: {results.sessions.length}
            </Typography>
          </Paper>

          {results.sessions.length === 0 ? (
            <Alert severity="info">
              No test sessions found. Complete a test to see your results here.
            </Alert>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {results.sessions.map((session) => (
                <Card key={session.session_uid} elevation={2}>
                  <CardContent>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginBottom: 2,
                      }}
                    >
                      <div>
                        <Typography variant="h6">
                          Session: {new Date(session.started_at || "").toLocaleDateString("de-DE")}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          Started: {formatDate(session.started_at)}
                          {session.stopped_at && ` • Stopped: ${formatDate(session.stopped_at)}`}
                        </Typography>
                        {session.intake && (
                          <Typography
                            variant="body2"
                            color="textSecondary"
                            style={{ marginTop: "4px" }}
                          >
                            ASRS-5 Score: {session.intake.total_score} (
                            {session.intake.symptom_group})
                          </Typography>
                        )}
                      </div>
                      <Button
                        variant="contained"
                        onClick={() => navigate(`/results/${session.session_uid}`)}
                      >
                        View Details
                      </Button>
                    </Box>
                    {session.features && (
                      <Box
                        sx={{
                          marginTop: 2,
                          padding: 2,
                          backgroundColor: "#fafafa",
                          borderRadius: 1,
                        }}
                      >
                        <Typography variant="subtitle2" gutterBottom>
                          Quick Summary:
                        </Typography>
                        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, marginTop: 1 }}>
                          {session.features.fixation_count !== null && (
                            <Typography variant="body2">
                              <strong>Fixations:</strong> {session.features.fixation_count}
                            </Typography>
                          )}
                          {session.features.saccade_count !== null && (
                            <Typography variant="body2">
                              <strong>Saccades:</strong> {session.features.saccade_count}
                            </Typography>
                          )}
                          {session.features.go_reaction_time_mean !== null && (
                            <Typography variant="body2">
                              <strong>Avg RT:</strong>{" "}
                              {session.features.go_reaction_time_mean.toFixed(2)}s
                            </Typography>
                          )}
                          {session.features.omission_errors !== null && (
                            <Typography variant="body2">
                              <strong>Omission Errors:</strong> {session.features.omission_errors}
                            </Typography>
                          )}
                          {session.features.commission_errors !== null && (
                            <Typography variant="body2">
                              <strong>Commission Errors:</strong>{" "}
                              {session.features.commission_errors}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
