import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import CircularProgress from "@mui/material/CircularProgress";
import CheckIcon from "@mui/icons-material/Check";
import GenericIcon from "../components/GenericIcon";
import styles from "./SingleResultPage.module.css";

interface SessionFeatureData {
  session_uid: string;
  user_id: number;
  mean_fixation_duration: number | null;
  fixation_count: number | null;
  gaze_dispersion: number | null;
  saccade_count: number | null;
  saccade_rate: number | null;
  total_blinks: number | null;
  blink_rate: number | null;
  go_reaction_time_mean: number | null;
  go_reaction_time_sd: number | null;
  omission_errors: number | null;
  commission_errors: number | null;
  go_trial_count?: number;
  nogo_trial_count?: number;
  started_at?: string;
  stopped_at?: string | null;
  name?: string;
  birthdate?: string;
}

const METRICS = [
  {
    key: "mean_fixation_duration",
    label: "Mean Fixation Duration",
    norm: "0.15 – 0.30 s",
    flag: (v: number) => v !== null && v >= 0.15 && v <= 0.3,
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v.toFixed(2)} s` : "-"),
  },
  {
    key: "fixation_count",
    label: "Fixation Count",
    norm: "900 – 1,200 fixations/session",
    flag: (v: number) => v !== null && v >= 900 && v <= 1200,
    format: (v: number | null) => (v !== null && !isNaN(v) ? v : "-"),
  },
  {
    key: "gaze_dispersion",
    label: "Gaze Dispersion",
    norm: "< 50 px",
    flag: (v: number) => (v !== null && v < 50 ? true : v !== null ? "high" : null),
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v} px` : "-"),
  },
  {
    key: "saccade_count",
    label: "Saccade Count",
    norm: "300 – 900 saccades/session",
    flag: (v: number) => v !== null && v >= 300 && v <= 900,
    format: (v: number | null) => (v !== null && !isNaN(v) ? v : "-"),
  },
  {
    key: "saccade_rate",
    label: "Saccade Rate",
    norm: "1 – 3 Hz",
    flag: (v: number) => v !== null && v >= 1 && v <= 3,
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v.toFixed(1)} Hz` : "-"),
  },
  {
    key: "total_blinks",
    label: "Total Blinks",
    norm: "30 – 45 blinks/session",
    flag: (v: number) => v !== null && v >= 30 && v <= 45,
    format: (v: number | null) => (v !== null && !isNaN(v) ? v : "-"),
  },
  {
    key: "blink_rate",
    label: "Blink Rate",
    norm: "0.10 – 0.15 Hz",
    flag: (v: number) => v !== null && v >= 0.1 && v <= 0.15,
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v.toFixed(2)} Hz` : "-"),
  },
  {
    key: "go_reaction_time_mean",
    label: "Go RT Mean",
    norm: "0.25 – 0.35 s",
    flag: (v: number) => v !== null && v >= 0.25 && v <= 0.35,
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v.toFixed(2)} s` : "-"),
  },
  {
    key: "go_reaction_time_sd",
    label: "Go RT SD",
    norm: "0.04 – 0.06 s",
    flag: (v: number) => v !== null && v >= 0.04 && v <= 0.06,
    format: (v: number | null) => (v !== null && !isNaN(v) ? `${v.toFixed(3)} s` : "-"),
  },
  {
    key: "omission_errors",
    label: "Omission Errors",
    norm: "0 – 4 omissions (0–5 % of Go trials)",
    flag: (v: number, d: any) => {
      // d is the data object
      if (d && d.go_trial_count !== undefined) {
        const errorCount = v !== null ? v : 0;
        return errorCount >= 0 && errorCount <= 4;
      }
      return null;
    },
    format: (v: number | null, d: any) => {
      const errorCount = v !== null ? v : 0;
      if (d && d.go_trial_count !== undefined) {
        return `${errorCount} / ${d.go_trial_count}`;
      }
      return errorCount.toString();
    },
  },
  {
    key: "commission_errors",
    label: "Commission Errors",
    norm: "0 – 1 commissions (0–5 % of No-Go)",
    flag: (v: number, d: any) => {
      if (d && d.nogo_trial_count !== undefined) {
        const errorCount = v !== null ? v : 0;
        return errorCount <= 1;
      }
      return null;
    },
    format: (v: number | null, d: any) => {
      const errorCount = v !== null ? v : 0;
      if (d && d.nogo_trial_count !== undefined) {
        return `${errorCount} / ${d.nogo_trial_count}`;
      }
      // If trial count is missing, just show the error count
      return errorCount.toString();
    },
  },
];

const SingleResultPage = () => {
  const { sessionUid } = useParams();
  const [data, setData] = useState<SessionFeatureData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionUid) return;
    setLoading(true);
    fetch(
      `${import.meta.env.VITE_API_URL || "http://20.74.82.26:8000"}/features/sessions/${sessionUid}`
    )
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch result");
        return res.json();
      })
      .then((d) => {
        setData(d);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [sessionUid]);

  const getAge = (dobString: string) => {
    const [year, month, day] = dobString.split("-").map(Number);
    const dobDate = new Date(Date.UTC(year, month - 1, day));
    const today = new Date();
    let age = today.getUTCFullYear() - dobDate.getUTCFullYear();
    const m = today.getUTCMonth() - dobDate.getUTCMonth();
    if (m < 0 || (m === 0 && today.getUTCDate() < dobDate.getUTCDate())) {
      age--;
    }
    return age;
  };

  return (
    <div className={styles.root}>
      <div className={styles.headerInfo}>
        <div className={styles.headerInfoRow}>
          <div>
            <strong>Name:</strong> {data?.name || "—"}
          </div>
          <div>
            <strong>Date of Birth:</strong>{" "}
            {data?.birthdate
              ? new Date(data.birthdate).toLocaleDateString("de-DE", {
                  day: "2-digit",
                  month: "2-digit",
                  year: "numeric",
                })
              : "—"}
          </div>
          <div>
            <strong>Age:</strong> {data?.birthdate ? getAge(data.birthdate) : "—"}
          </div>
          <div>
            <strong>User ID:</strong> {data?.user_id || "—"}
          </div>
          <div>
            <strong>Time of Session:</strong>{" "}
            {data?.started_at
              ? `
                                ${new Date(data.started_at).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" })} at 
                                ${new Date(data.started_at).toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" })}
                            `
              : "—"}
          </div>
        </div>
      </div>
      <TableContainer component={Paper} className={styles.tableContainer}>
        <Table>
          <TableHead className={styles.tableHead}>
            <TableRow>
              <TableCell>
                <strong>Metric</strong>
              </TableCell>
              <TableCell>
                <strong>Patient's Value</strong>
              </TableCell>
              <TableCell>
                <strong>Normative Range</strong>
              </TableCell>
              <TableCell>
                <strong>Flag</strong>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} align="center">
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : error ? (
              <TableRow>
                <TableCell colSpan={4} align="center" style={{ color: "red" }}>
                  {error}
                </TableCell>
              </TableRow>
            ) : (
              METRICS.map((metric) => {
                const rawValue = data ? data[metric.key as keyof SessionFeatureData] : null;
                const value = typeof rawValue === "number" || rawValue === null ? rawValue : null;
                let flag = null;
                if (metric.key === "gaze_dispersion" && typeof value === "number") {
                  if (value < 50) {
                    flag = <CheckIcon color="success" />;
                  } else {
                    // deviation from 50
                    const deviation = ((value - 50) / 50) * 100;
                    const color = deviation < 10 ? "yellow" : "red";
                    flag = <GenericIcon icon="flag" fill={color} />;
                  }
                } else if (
                  metric.key === "commission_errors" &&
                  typeof value === "number" &&
                  data &&
                  typeof data.nogo_trial_count === "number"
                ) {
                  const max = 1;
                  if (value <= max) {
                    flag = <CheckIcon color="success" />;
                  } else {
                    const deviation = ((value - max) / (data.nogo_trial_count || 1)) * 100;
                    const color = deviation < 10 ? "yellow" : "red";
                    flag = <GenericIcon icon="flag" fill={color} />;
                  }
                } else if (
                  metric.key === "omission_errors" &&
                  typeof value === "number" &&
                  data &&
                  typeof data.go_trial_count === "number"
                ) {
                  const max = 4;
                  if (value <= max) {
                    flag = <CheckIcon color="success" />;
                  } else {
                    const deviation = ((value - max) / (data.go_trial_count || 1)) * 100;
                    const color = deviation < 10 ? "yellow" : "red";
                    flag = <GenericIcon icon="flag" fill={color} />;
                  }
                } else if (typeof value === "number" && metric.flag) {
                  // For range metrics
                  const inRange = metric.flag(value, data);
                  if (inRange) {
                    flag = <CheckIcon color="success" />;
                  } else {
                    // Find the nearest bound
                    let lower = null,
                      upper = null;
                    if (metric.norm.includes("–")) {
                      const parts = metric.norm
                        .split("–")
                        .map((s) => s.replace(/[^\d.]/g, "").trim());
                      if (parts.length === 2) {
                        lower = parseFloat(parts[0]);
                        upper = parseFloat(parts[1]);
                      }
                    }
                    if (lower !== null && upper !== null) {
                      let deviation = 0;
                      if (value < lower) deviation = ((lower - value) / lower) * 100;
                      else if (value > upper) deviation = ((value - upper) / upper) * 100;
                      const color = deviation < 10 ? "yellow" : "red";
                      flag = <GenericIcon icon="flag" fill={color} />;
                    } else {
                      flag = <GenericIcon icon="flag" fill="yellow" />;
                    }
                  }
                }
                const displayValue = typeof value === "number" && !isNaN(value) ? value : null;
                return (
                  <TableRow key={metric.key}>
                    <TableCell>{metric.label}</TableCell>
                    <TableCell>{metric.format(displayValue, data)}</TableCell>
                    <TableCell>{metric.norm}</TableCell>
                    <TableCell>{flag}</TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default SingleResultPage;
