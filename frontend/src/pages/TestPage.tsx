import { FC, useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./TestPage.module.css";
import EscapeConfirmationModal from "../components/modals/EscapeConfirmationModal";
import AgentInstallModal from "../components/modals/AgentInstallModal";
import AgentStatusChecker from "../components/AgentStatusChecker";
import { ASRS_QUESTIONS, ASRS_OPTIONS } from "./IntakeQuestionnairePage";

const CONFIG = {
  RESPONSE_TIME_LIMIT: 2000,
  STIMULUS_DISPLAY_TIME: 2000,
  FEEDBACK_DISPLAY_TIME: 1000,
  PRACTICE_TRIALS: 10,
  MAIN_TEST_TRIALS: 100,
  GO_TRIAL_PERCENTAGE: 0.8,
  ESCAPE_CONFIRMATION_TIME: 5000,
  CALIBRATION_POINT_DURATION: 1000,
  API_BASE_URL: "http://localhost:8000",
  AGENT_BASE_URL: "http://localhost:9000",
} as const;

type TestPhase =
  | "instructions"
  | "calibration"
  | "practice"
  | "main-test"
  | "complete"
  | "practice-complete";
// 0 = instructions, 1-8 = individual dots, 9 = completion
type CalibrationStep = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
type TrialType = "go" | "nogo";
type TrialResult = "correct" | "too-slow" | "false-alarm" | "pending";

interface Trial {
  id: number;
  type: TrialType;
  stimulus: string;
  result: TrialResult;
  responseTime?: number;
}

interface CalibrationPoint {
  x: number;
  y: number;
}

const TestPage: FC = () => {
  const [phase, setPhase] = useState<TestPhase>("instructions");
  const [calibrationStep, setCalibrationStep] = useState<CalibrationStep>(0);
  const [currentTrial, setCurrentTrial] = useState<Trial | null>(null);
  const [trialIndex, setTrialIndex] = useState(0);
  const [trials, setTrials] = useState<Trial[]>([]);
  const [isPractice, setIsPractice] = useState(false);
  const [trialStartTime, setTrialStartTime] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [keyPressed, setKeyPressed] = useState(false);
  const [escapePressed, setEscapePressed] = useState(false);
  const [showEscapeConfirmation, setShowEscapeConfirmation] = useState(false);

  // Backend integration state
  const [sessionUid, setSessionUid] = useState<string | null>(null);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [calibrationError, setCalibrationError] = useState<string | null>(null);
  const [acquisitionStarted, setAcquisitionStarted] = useState(false);
  const [isStartingTest, setIsStartingTest] = useState(false);

  // Agent status state
  const [agentConnected, setAgentConnected] = useState(false);
  const [showAgentInstallModal, setShowAgentInstallModal] = useState(false);

  const navigate = useNavigate();
  const [showIntakeModal, setShowIntakeModal] = useState(false);
  const [intakeData, setIntakeData] = useState<any | null>(null);

  // Calibration dots positions (corners of screen) - clockwise order starting from top-left
  const calibrationDots: CalibrationPoint[] = [
    { x: 10, y: 10 }, // Top-left
    { x: 50, y: 10 }, // Top-center
    { x: 90, y: 10 }, // Top-right
    { x: 90, y: 50 }, // Right-center
    { x: 90, y: 90 }, // Bottom-right
    { x: 50, y: 90 }, // Bottom-center
    { x: 10, y: 90 }, // Bottom-left
    { x: 10, y: 50 }, // Left-center
  ];

  // API helper functions
  const apiCall = async (url: string, options: RequestInit = {}) => {
    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`
                    API call failed: ${response.status} ${response.statusText}
                `);
      }

      return await response.json();
    } catch (error) {
      console.error("API call error:", error);
      throw error;
    }
  };

  const startCalibration = async () => {
    // Check if agent is connected first
    if (!agentConnected) {
      setShowAgentInstallModal(true);
      return;
    }

    try {
      setIsCalibrating(true);
      setCalibrationError(null);
      await apiCall(`${CONFIG.AGENT_BASE_URL}/calibrate/start`, {
        method: "POST",
      });
      console.log("Calibration started successfully");
    } catch (error) {
      console.error("Failed to start calibration:", error);
      setCalibrationError(
        "Failed to start calibration. Please check if the backend and local agent are running."
      );
    } finally {
      setIsCalibrating(false);
    }
  };

  const recordCalibrationPoint = async (point: CalibrationPoint) => {
    try {
      const response = await apiCall(`${CONFIG.AGENT_BASE_URL}/calibrate/point`, {
        method: "POST",
        body: JSON.stringify({
          session_uid: sessionUid,
          x: point.x,
          y: point.y,
          duration: CONFIG.CALIBRATION_POINT_DURATION / 1000,
          samples: 30,
        }),
      });

      console.log("Calibration point recorded:", response);
      return response;
    } catch (error) {
      console.error("Failed to record calibration point:", error);
      throw error;
    }
  };

  const finishCalibration = async () => {
    try {
      const response = await apiCall(`${CONFIG.AGENT_BASE_URL}/calibrate/finish`, {
        method: "POST",
      });

      console.log("Calibration finished:", response);
      return response;
    } catch (error) {
      console.error("Failed to finish calibration:", error);
      throw error;
    }
  };

  const startSession = async () => {
    try {
      const response = await apiCall(`${CONFIG.API_BASE_URL}/session/start`, {
        method: "POST",
        body: JSON.stringify({ session_uid: sessionUid }),
      });
      console.log("Session started:", response);
      return response;
    } catch (error) {
      console.error("Failed to start session:", error);
      throw error;
    }
  };

  const startAcquisition = async (acqSessionUid?: string) => {
    try {
      const response = await apiCall(`${CONFIG.AGENT_BASE_URL}/start`, {
        method: "POST",
        body: JSON.stringify({
          session_uid: acqSessionUid || sessionUid,
          api_url: `${CONFIG.API_BASE_URL}/acquisition/batch`,
          fps: 20.0,
        }),
      });
      console.log("Acquisition started:", response);
      setAcquisitionStarted(true);
      return response;
    } catch (error) {
      console.error("Failed to start acquisition:", error);
      throw error;
    }
  };

  const stopAcquisition = async () => {
    try {
      const response = await apiCall(`${CONFIG.AGENT_BASE_URL}/stop`, {
        method: "POST",
      });

      console.log("Acquisition stopped:", response);
      setAcquisitionStarted(false);
      return response;
    } catch (error) {
      console.error("Failed to stop acquisition:", error);
      throw error;
    }
  };

  const stopSession = async () => {
    try {
      const response = await apiCall(`${CONFIG.API_BASE_URL}/session/stop`, {
        method: "POST",
      });

      console.log("Session stopped:", response);
      return response;
    } catch (error) {
      console.error("Failed to stop session:", error);
      throw error;
    }
  };

  const computeSessionFeatures = async () => {
    if (!sessionUid) return;

    try {
      const response = await apiCall(`${CONFIG.API_BASE_URL}/features/compute/${sessionUid}`, {
        method: "POST",
      });

      console.log("Session features computed:", response);
      return response;
    } catch (error) {
      console.error("Failed to compute session features:", error);
      throw error;
    }
  };

  const logStimulusOnset = async (stimulus: string) => {
    if (!sessionUid) return;

    try {
      await apiCall(`${CONFIG.API_BASE_URL}/session/event`, {
        method: "POST",
        body: JSON.stringify({
          session_uid: sessionUid,
          timestamp: Date.now() / 1000,
          event_type: "stimulus_onset",
          stimulus: stimulus,
        }),
      });
    } catch (error) {
      console.error("Failed to log stimulus onset:", error);
    }
  };

  const logResponse = async (stimulus: string, response: boolean) => {
    if (!sessionUid) return;

    try {
      await apiCall(`${CONFIG.API_BASE_URL}/session/event`, {
        method: "POST",
        body: JSON.stringify({
          session_uid: sessionUid,
          timestamp: Date.now() / 1000,
          event_type: "response",
          stimulus: stimulus,
          response: response,
        }),
      });
    } catch (error) {
      console.error("Failed to log response:", error);
    }
  };

  useEffect(() => {
    const intake = localStorage.getItem("asrs5-intake");
    if (intake) {
      const parsed = JSON.parse(intake);
      setIntakeData(parsed);
      setSessionUid(parsed.session_uid);
    }

    // Check agent status on page load
    const checkAgent = async () => {
      try {
        const response = await fetch(`${CONFIG.AGENT_BASE_URL}/status`, {
          signal: AbortSignal.timeout(2000),
        });
        if (response.ok) {
          setAgentConnected(true);
        }
      } catch (error) {
        // Agent not running
        setAgentConnected(false);
      }
    };
    checkAgent();
  }, []);

  const generateTrials = useCallback((count: number, isPractice: boolean = false) => {
    const newTrials: Trial[] = [];

    if (isPractice) {
      const goTrials = Math.floor(count * CONFIG.GO_TRIAL_PERCENTAGE);
      const nogoTrials = count - goTrials;

      // Generate Go trials
      for (let i = 0; i < goTrials; i++) {
        newTrials.push({
          id: i,
          type: "go",
          stimulus: getRandomLetter(),
          result: "pending",
        });
      }

      // Generate No-go trials (X)
      for (let i = 0; i < nogoTrials; i++) {
        newTrials.push({
          id: goTrials + i,
          type: "nogo",
          stimulus: "X",
          result: "pending",
        });
      }

      // Shuffle the trials
      for (let i = newTrials.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newTrials[i], newTrials[j]] = [newTrials[j], newTrials[i]];
      }
    } else {
      // For main test, use same deterministic approach as practice
      const goTrials = Math.floor(count * CONFIG.GO_TRIAL_PERCENTAGE);
      const nogoTrials = count - goTrials;

      // Generate Go trials
      for (let i = 0; i < goTrials; i++) {
        newTrials.push({
          id: i,
          type: "go",
          stimulus: getRandomLetter(),
          result: "pending",
        });
      }

      // Generate No-go trials (X)
      for (let i = 0; i < nogoTrials; i++) {
        newTrials.push({
          id: goTrials + i,
          type: "nogo",
          stimulus: "X",
          result: "pending",
        });
      }

      // Shuffle the trials
      for (let i = newTrials.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newTrials[i], newTrials[j]] = [newTrials[j], newTrials[i]];
      }
    }

    return newTrials;
  }, []);

  const getRandomLetter = () => {
    const letters = "ABCDEFGHIJKLMNOPQRSTUVWYZ"; // Excluding X
    return letters[Math.floor(Math.random() * letters.length)];
  };

  const handleEscapeCancel = useCallback(async () => {
    setShowEscapeConfirmation(false);
    setEscapePressed(false);
    try {
      await finishCalibration();
    } catch (e) {
      // no-op
    }
    window.location.href = "/";
  }, []);

  const handleEscapeContinue = useCallback(() => {
    setShowEscapeConfirmation(false);
    setEscapePressed(false);
  }, []);

  useEffect(() => {
    const handleKeyPress = async (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (!escapePressed) {
          setEscapePressed(true);
          setShowEscapeConfirmation(true);
        } else if (showEscapeConfirmation) {
          window.location.href = "/";
        }
        return;
      }

      if (event.key === "Enter" && showEscapeConfirmation) {
        setShowEscapeConfirmation(false);
        setEscapePressed(false);
        return;
      }

      if (showEscapeConfirmation) {
        return; // Block all other keys when escape confirmation is shown
      }

      if (event.key === "Enter" && phase === "instructions") {
        if (!agentConnected) {
          setShowAgentInstallModal(true);
          return;
        }
        await startCalibration();
        setPhase("calibration");
        setCalibrationStep(0);
      } else if (
        phase === "calibration" &&
        calibrationStep === 0 &&
        (event.key === "Enter" || event.key === " ")
      ) {
        setCalibrationStep(1);
      } else if (phase === "practice-complete") {
        if (event.key === "Enter") {
          startMainTest();
        }
      } else if (phase === "practice" || phase === "main-test") {
        if (event.key === " " && currentTrial && !keyPressed) {
          setKeyPressed(true);
          const responseTime = Date.now() - (trialStartTime || 0);

          if (currentTrial.type === "go") {
            if (responseTime <= CONFIG.RESPONSE_TIME_LIMIT) {
              currentTrial.result = "correct";
              if (isPractice) {
                setFeedbackMessage("✅ Correct");
              }
              if (!isPractice) {
                await logResponse(currentTrial.stimulus, true);
              }
            } else {
              currentTrial.result = "too-slow";
              if (isPractice) {
                setFeedbackMessage("❌ Too Slow");
              }
              if (!isPractice) {
                await logResponse(currentTrial.stimulus, false);
              }
            }
          } else {
            currentTrial.result = "false-alarm";
            if (isPractice) {
              setFeedbackMessage("❌ False Alarm");
            }
            if (!isPractice) {
              await logResponse(currentTrial.stimulus, false);
            }
          }

          currentTrial.responseTime = responseTime;

          if (isPractice) {
            setShowFeedback(true);
            setTimeout(() => {
              setShowFeedback(false);
              setKeyPressed(false);
              setCurrentTrial(null);
              nextTrial();
            }, CONFIG.FEEDBACK_DISPLAY_TIME);
          } else {
            setTimeout(() => {
              setKeyPressed(false);
              setCurrentTrial(null);
              setTrialIndex((prev) => {
                const nextIndex = prev + 1;
                if (nextIndex >= trials.length) {
                  setPhase(isPractice ? "practice-complete" : "complete");
                  return prev;
                }
                return nextIndex;
              });
            }, 500);
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, [
    phase,
    calibrationStep,
    currentTrial,
    keyPressed,
    trialStartTime,
    escapePressed,
    showEscapeConfirmation,
    sessionUid,
    isPractice,
    agentConnected,
    trials,
  ]);

  useEffect(() => {
    if (phase !== "calibration") return;
    if (calibrationStep < 1 || calibrationStep > 8) return;
    const doStep = async () => {
      try {
        const currentPoint = calibrationDots[calibrationStep - 1];
        await recordCalibrationPoint(currentPoint);
        if (calibrationStep < 8) {
          setTimeout(
            () => setCalibrationStep((calibrationStep + 1) as CalibrationStep),
            CONFIG.CALIBRATION_POINT_DURATION
          );
        } else {
          await finishCalibration();
          setTimeout(
            () => setCalibrationStep(9 as CalibrationStep),
            CONFIG.CALIBRATION_POINT_DURATION
          );
        }
      } catch (error) {
        setCalibrationError("Calibration failed. Please try again.");
      }
    };
    doStep();
    return undefined;
  }, [phase, calibrationStep]);

  // NOTE: Only for development purposes
  // useEffect(() => {
  //     if (phase === 'calibration' && calibrationStep === 0) {
  //         setCalibrationStep(9);
  //         finishCalibration();
  //     }
  // }, [phase, calibrationStep]);

  const startTrial = useCallback(async () => {
    if (trialIndex < trials.length) {
      const trial = trials[trialIndex];
      setCurrentTrial(trial);
      setTrialStartTime(Date.now());
      setKeyPressed(false);

      if (!isPractice) {
        await logStimulusOnset(trial.stimulus);
      }
    }
  }, [trialIndex, trials, sessionUid, isPractice]);

  const nextTrial = () => {
    setTrialIndex((prev) => {
      const nextIndex = prev + 1;
      if (nextIndex >= trials.length) {
        if (isPractice) {
          setPhase("practice-complete");
        } else {
          setPhase("complete");
        }
        return prev;
      }
      return nextIndex;
    });
  };

  const startPractice = async () => {
    setIsPractice(true);
    setTrials(generateTrials(CONFIG.PRACTICE_TRIALS, true));
    setTrialIndex(0);
    setPhase("practice");
  };

  const startMainTest = async () => {
    try {
      setIsStartingTest(true);
      setCalibrationError(null);

      // Step 1: Start session
      console.log("Starting session...");
      const sessionResponse = await startSession();
      const newSessionUid = sessionResponse.session_uid;
      setSessionUid(newSessionUid);

      // Step 2: Pause and verify camera is ready
      console.log("Verifying camera initialization...");
      await new Promise((resolve) => setTimeout(resolve, 2000)); // 2 second pause

      // Step 3: Start acquisition with verification
      console.log("Starting acquisition...");
      const acquisitionResponse = await startAcquisition(newSessionUid);

      // Step 4: Additional pause to ensure acquisition is stable
      console.log("Stabilizing acquisition...");
      await new Promise((resolve) => setTimeout(resolve, 1000)); // 1 second pause

      // Step 5: Start the test
      setIsPractice(false);
      setTrials(generateTrials(CONFIG.MAIN_TEST_TRIALS));
      setTrialIndex(0);
      setPhase("main-test");
    } catch (error) {
      console.error("Failed to start main test:", error);
      setCalibrationError(
        "Failed to start main test. Please check if the camera is properly connected and try again."
      );
    } finally {
      setIsStartingTest(false);
    }
  };

  useEffect(() => {
    if (trialIndex < trials.length && (phase === "practice" || phase === "main-test")) {
      startTrial();
    }
  }, [trialIndex, phase, trials.length, startTrial]);

  const nextTrialCb = useCallback(() => {
    setTrialIndex((i) => {
      const ni = i + 1;
      if (ni >= trials.length) {
        setPhase(isPractice ? "practice-complete" : "complete");
        return i;
      }
      return ni;
    });
  }, [isPractice, trials.length]);

  useEffect(() => {
    if ((phase === "practice" || phase === "main-test") && currentTrial) {
      const timer = setTimeout(async () => {
        if (currentTrial.type === "nogo") {
          // No-Go: user did NOT press spacebar (correct)
          setTrials((ts) =>
            ts.map((t) => (t.id === currentTrial.id ? { ...t, result: "correct" } : t))
          );
          if (!isPractice) {
            await logResponse(currentTrial.stimulus, true); // did not press = true
          }
        } else {
          // Go: user did NOT press spacebar (too slow)
          setTrials((ts) =>
            ts.map((t) => (t.id === currentTrial.id ? { ...t, result: "too-slow" } : t))
          );
          if (!isPractice) {
            await logResponse(currentTrial.stimulus, false); // did not press = false
          }
        }

        if (isPractice) {
          const message = currentTrial.type === "nogo" ? "✅ Correct" : "❌ Too Slow";
          setFeedbackMessage(message);
          setShowFeedback(true);
          setTimeout(() => {
            setShowFeedback(false);
            setCurrentTrial(null);
            nextTrialCb();
          }, CONFIG.FEEDBACK_DISPLAY_TIME);
        } else {
          setCurrentTrial(null);
          nextTrialCb();
        }
      }, CONFIG.STIMULUS_DISPLAY_TIME);
      return () => clearTimeout(timer);
    }
  }, [currentTrial, isPractice, phase, nextTrialCb]);

  const cleanupTest = useCallback(async () => {
    let stopSessionError = null;
    try {
      if (acquisitionStarted) {
        await stopAcquisition();
      }
      try {
        await stopSession();
      } catch (error) {
        stopSessionError = error;
        console.error("Failed to stop session:", error);
      }
      await computeSessionFeatures();
    } catch (error) {
      console.error("Failed to cleanup test:", error);
      // Still try to compute features if not already attempted
      if (!stopSessionError) {
        await computeSessionFeatures();
      }
    }
  }, [acquisitionStarted, sessionUid]);

  useEffect(() => {
    if (phase === "complete" && trials.length > 0 && !isPractice) {
      cleanupTest();
    }
  }, [phase, cleanupTest, trials.length, isPractice]);

  if (!intakeData) {
    return (
      <div className={styles.container}>
        <div className={styles.modal}>
          <h1>Go/No-Go Test Instructions</h1>
          <TestInstructions showQuestionnaireButton={true} />
        </div>
      </div>
    );
  }

  const handleRetake = () => {
    localStorage.removeItem("asrs5-intake");
    setIntakeData(null);
    navigate("/intake");
  };

  if (phase === "instructions") {
    return (
      <div className={styles.container}>
        <div className={styles.modal}>
          <h1>Go/No-Go Test Instructions</h1>

          {/* Agent Status Checker */}
          <div style={{ marginBottom: "20px" }}>
            <AgentStatusChecker
              agentUrl={CONFIG.AGENT_BASE_URL}
              onAgentReady={() => setAgentConnected(true)}
              showDownloadButton={true}
            />
          </div>

          <TestInstructions
            showActionButtons={true}
            onViewResults={() => setShowIntakeModal(true)}
            onRetake={handleRetake}
            onProceed={async () => {
              if (!agentConnected) {
                setShowAgentInstallModal(true);
                return;
              }
              await startCalibration();
              setPhase("calibration");
            }}
          />
        </div>

        {/* Agent Install Modal */}
        <AgentInstallModal
          open={showAgentInstallModal}
          onClose={() => setShowAgentInstallModal(false)}
          agentUrl={CONFIG.AGENT_BASE_URL}
          onAgentReady={() => {
            setAgentConnected(true);
            setShowAgentInstallModal(false);
          }}
        />

        {showIntakeModal && (
          <div className={styles.intakeModalOverlay}>
            <div className={styles.intakeModal}>
              <h2>Previous Questionnaire Results</h2>
              <div className={styles.intakeUserInfo}>
                <div className={styles.intakeUserField}>
                  <strong>Name:</strong> {intakeData.name}
                </div>
                <div className={styles.intakeUserField}>
                  <strong>Birthdate:</strong> {new Date(intakeData.birthdate).toLocaleDateString()}
                </div>
                <div className={styles.intakeUserField}>
                  <strong>Completed:</strong> {new Date(intakeData.timestamp).toLocaleString()}
                </div>
              </div>
              <div className={styles.intakeResultsScrollable}>
                {ASRS_QUESTIONS.map((q, idx) => (
                  <div key={q.id} className={styles.intakeResultQA}>
                    <div className={styles.intakeResultQuestion}>
                      <strong>Q{idx + 1}:</strong> {q.text}
                    </div>
                    <div className={styles.intakeResultAnswer}>
                      <em>{ASRS_OPTIONS[intakeData.answers[idx]]}</em>
                    </div>
                  </div>
                ))}
              </div>
              <button className={styles.button} onClick={() => setShowIntakeModal(false)}>
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (phase === "calibration") {
    return (
      <div className={styles.container}>
        <div className={styles.calibrationGrid}>
          {calibrationStep > 0 && calibrationStep <= 8 && (
            <div
              className={styles.calibrationDot}
              style={{
                left: `${calibrationDots[calibrationStep - 1].x}%`,
                top: `${calibrationDots[calibrationStep - 1].y}%`,
              }}
            />
          )}
        </div>

        {calibrationStep === 0 && (
          <div className={styles.calibrationInstructions}>
            <h2>Calibration</h2>
            <p>We need to calibrate your gaze. Please follow the dots as they appear.</p>
            <p>
              Press <strong>[Space]</strong> or <strong>[Enter]</strong> to start.
            </p>

            {calibrationError && <div className={styles.errorMessage}>{calibrationError}</div>}

            <p>Tips:</p>
            <ul>
              <li>
                Please make sure the monitor with the webcam is in the center of your field of view,
                {"\u00A0"}
                and is the same as the one you are looking at.
              </li>
              <li>
                Press <strong>[Escape]</strong> at any time to stop the process.
              </li>
            </ul>
          </div>
        )}

        {calibrationStep === 9 && (
          <div className={styles.calibrationComplete}>
            <h2>Calibration Complete</h2>
            {isStartingTest ? (
              <div className={styles.loadingMessage}>
                <p>Initializing camera and starting test...</p>
                <p>Please wait while we verify the camera connection.</p>
                {calibrationError && <div className={styles.errorMessage}>{calibrationError}</div>}
              </div>
            ) : (
              <div className={styles.calibrationButtons}>
                <button onClick={startPractice} className={styles.button}>
                  Do a practice
                </button>
                <button onClick={startMainTest} className={styles.button}>
                  Proceed to main exam
                </button>
              </div>
            )}
          </div>
        )}

        {calibrationStep > 0 && calibrationStep < 9 && (
          <div className={styles.calibrationProgress}>
            <p>Dot {calibrationStep} of 8</p>
          </div>
        )}

        <EscapeConfirmationModal
          show={showEscapeConfirmation}
          onCancel={handleEscapeCancel}
          onContinue={handleEscapeContinue}
        />
      </div>
    );
  }

  if (phase === "practice" || phase === "main-test") {
    return (
      <div className={styles.container}>
        {currentTrial && !showFeedback && (
          <div className={styles.stimulus}>
            <span className={styles.letter}>{currentTrial.stimulus}</span>
          </div>
        )}

        {showFeedback && (
          <div className={styles.feedback}>
            <span className={styles.feedbackMessage}>{feedbackMessage}</span>
          </div>
        )}

        <EscapeConfirmationModal
          show={showEscapeConfirmation}
          onCancel={handleEscapeCancel}
          onContinue={handleEscapeContinue}
        />
      </div>
    );
  }

  if (phase === "complete") {
    const correctTrials = trials.filter((t) => t.result === "correct").length;
    const accuracy = (correctTrials / trials.length) * 100;

    return (
      <div className={styles.container}>
        <div className={styles.modal}>
          <h1>Test Complete!</h1>
          <div className={styles.results}>
            <p>Accuracy: {accuracy.toFixed(1)}%</p>
            <p>
              Correct responses: {correctTrials} / {trials.length}
            </p>
          </div>
          <button onClick={() => navigate(`/results/${sessionUid}`)} className={styles.button}>
            View Detailed Results
          </button>
        </div>
        <EscapeConfirmationModal
          show={showEscapeConfirmation}
          onCancel={handleEscapeCancel}
          onContinue={handleEscapeContinue}
        />
      </div>
    );
  }

  if (phase === "practice-complete") {
    return (
      <div className={styles.container}>
        <div className={styles.modal}>
          <h1>End of Practice</h1>
          <div className={styles.instructions}>
            <p>You have completed the practice trials.</p>
            <p className={styles.readyText}>
              Press <strong>[Enter]</strong> to begin the main test.
            </p>
          </div>
        </div>
        <EscapeConfirmationModal
          show={showEscapeConfirmation}
          onCancel={handleEscapeCancel}
          onContinue={handleEscapeContinue}
        />
      </div>
    );
  }

  return null;
};

export default TestPage;

// ================================
// UTILITY COMPONENTS FOR TEST PAGE
// ================================

const TestInstructions: FC<{
  showQuestionnaireButton?: boolean;
  showActionButtons?: boolean;
  onViewResults?: () => void;
  onRetake?: () => void;
  onProceed?: () => void;
}> = ({
  showQuestionnaireButton = false,
  showActionButtons = false,
  onViewResults,
  onRetake,
  onProceed,
}) => (
  <div className={styles.instructions}>
    <p>
      <strong>You will see letters one at a time.</strong>
    </p>
    <ul>
      <li>
        If you see any letter, symbol or number that is <strong>not X</strong> (Go),
        {"\u00A0"}
        press the <strong>[spacebar]</strong> as quickly as you can.
      </li>
      <li>
        If you see <strong>X</strong> (No-Go), withhold your response.
      </li>
    </ul>
    <p>
      There will be 100 trials, lasting about 2 minutes. You can practice 10 before beginning the
      test.
    </p>

    {showQuestionnaireButton && (
      <>
        <p className={styles.readyText}>
          Press the button below to answer a few questions before starting the test.
        </p>
        <div className={styles.takeQuestionnaireButtonContainer}>
          <Link to="/intake" className={styles.button}>
            Take Questionnaire
          </Link>
        </div>
      </>
    )}

    {showActionButtons && (
      <>
        <p className={styles.readyText}>
          It seems you have already answered the ASRS questionnaire.
        </p>
        <div style={{ display: "flex", gap: 16, marginTop: 24 }}>
          <button className={`${styles.button} ${styles.secondaryButton}`} onClick={onViewResults}>
            View Previous Results
          </button>
          <button className={`${styles.button} ${styles.secondaryButton}`} onClick={onRetake}>
            Answer Again
          </button>
          <button className={styles.button} onClick={onProceed}>
            Proceed to Calibration
          </button>
        </div>
      </>
    )}
  </div>
);
