import { FC, useState, useEffect, useCallback } from 'react';
import styles from './TestPage.module.css';
import EscapeConfirmationModal from '../components/modals/EscapeConfirmationModal';

const CONFIG = {
    RESPONSE_TIME_LIMIT: 5000,
    NO_GO_DISPLAY_TIME: 5000,
    FEEDBACK_DISPLAY_TIME: 1000,
    PRACTICE_TRIALS: 10,
    MAIN_TEST_TRIALS: 100,
    GO_TRIAL_PERCENTAGE: 0.8,
    ESCAPE_CONFIRMATION_TIME: 5000,
} as const;

type TestPhase = 'instructions' | 'calibration' | 'practice' | 'main-test' | 'complete' | 'practice-complete';
type CalibrationStep = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9; // 0 = instructions, 1-8 = individual dots, 9 = completion
type TrialType = 'go' | 'nogo';
type TrialResult = 'correct' | 'too-slow' | 'false-alarm' | 'pending';

interface Trial {
    id: number;
    type: TrialType;
    stimulus: string;
    result: TrialResult;
    responseTime?: number;
}

const TestPage: FC = () => {
    const [phase, setPhase] = useState<TestPhase>('instructions');
    const [calibrationStep, setCalibrationStep] = useState<CalibrationStep>(0);
    const [currentTrial, setCurrentTrial] = useState<Trial | null>(null);
    const [trialIndex, setTrialIndex] = useState(0);
    const [trials, setTrials] = useState<Trial[]>([]);
    const [isPractice, setIsPractice] = useState(false);
    const [trialStartTime, setTrialStartTime] = useState<number | null>(null);
    const [showFeedback, setShowFeedback] = useState(false);
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const [keyPressed, setKeyPressed] = useState(false);
    const [escapePressed, setEscapePressed] = useState(false);
    const [showEscapeConfirmation, setShowEscapeConfirmation] = useState(false);

    // Calibration dots positions (corners of screen) - clockwise order starting from top-left
    const calibrationDots = [
        { x: 10, y: 10 },   // Top-left
        { x: 50, y: 10 },   // Top-center
        { x: 90, y: 10 },   // Top-right
        { x: 90, y: 50 },   // Right-center
        { x: 90, y: 90 },   // Bottom-right
        { x: 50, y: 90 },   // Bottom-center
        { x: 10, y: 90 },   // Bottom-left
        { x: 10, y: 50 },   // Left-center
    ];

    const generateTrials = useCallback((count: number, isPractice: boolean = false) => {
        const newTrials: Trial[] = [];

        if (isPractice) {
            // For practice, ensure at least 2 X trials
            const goTrials = Math.floor(count * CONFIG.GO_TRIAL_PERCENTAGE);
            const nogoTrials = count - goTrials;

            // Generate Go trials
            for (let i = 0; i < goTrials; i++) {
                newTrials.push({
                    id: i,
                    type: 'go',
                    stimulus: getRandomLetter(),
                    result: 'pending'
                });
            }

            // Generate No-go trials (X)
            for (let i = 0; i < nogoTrials; i++) {
                newTrials.push({
                    id: goTrials + i,
                    type: 'nogo',
                    stimulus: 'X',
                    result: 'pending'
                });
            }

            // Shuffle the trials
            for (let i = newTrials.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [newTrials[i], newTrials[j]] = [newTrials[j], newTrials[i]];
            }
        } else {
            // For main test, use random distribution
            for (let i = 0; i < count; i++) {
                const isGo = Math.random() < CONFIG.GO_TRIAL_PERCENTAGE;
                newTrials.push({
                    id: i,
                    type: isGo ? 'go' : 'nogo',
                    stimulus: isGo ? getRandomLetter() : 'X',
                    result: 'pending'
                });
            }
        }

        return newTrials;
    }, []);

    const getRandomLetter = () => {
        const letters = 'ABCDEFGHIJKLMNOPQRSTUVWYZ'; // Excluding X
        return letters[Math.floor(Math.random() * letters.length)];
    };

    const handleEscapeCancel = useCallback(() => {
        setShowEscapeConfirmation(false);
        setEscapePressed(false);
        window.location.href = '/';
    }, []);

    const handleEscapeContinue = useCallback(() => {
        setShowEscapeConfirmation(false);
        setEscapePressed(false);
    }, []);

    useEffect(() => {
        const handleKeyPress = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                if (!escapePressed) {
                    setEscapePressed(true);
                    setShowEscapeConfirmation(true);
                } else if (showEscapeConfirmation) {
                    window.location.href = '/';
                }
                return;
            }

            if (event.key === 'Enter' && showEscapeConfirmation) {
                setShowEscapeConfirmation(false);
                setEscapePressed(false);
                return;
            }

            if (showEscapeConfirmation) {
                return; // Block all other keys when escape confirmation is shown
            }

            if (event.key === 'Enter' && phase === 'instructions') {
                setPhase('calibration');
                setCalibrationStep(0);
            } else if (phase === 'calibration') {
                if (event.key === 'Enter' || event.key === ' ') {
                    if (calibrationStep < 8) {
                        setCalibrationStep((calibrationStep + 1) as CalibrationStep);
                    } else if (calibrationStep === 8) {
                        setCalibrationStep(9 as CalibrationStep);
                    }
                }
            } else if (phase === 'practice-complete') {
                if (event.key === 'Enter') {
                    startMainTest();
                }
            } else if (phase === 'practice' || phase === 'main-test') {
                if (event.key === ' ' && currentTrial && !keyPressed) {
                    setKeyPressed(true);
                    const responseTime = Date.now() - (trialStartTime || 0);

                    if (currentTrial.type === 'go') {
                        if (responseTime <= CONFIG.RESPONSE_TIME_LIMIT) {
                            currentTrial.result = 'correct';
                            if (isPractice) {
                                setFeedbackMessage('✅ Correct');
                            }
                        } else {
                            currentTrial.result = 'too-slow';
                            if (isPractice) {
                                setFeedbackMessage('❌ Too Slow');
                            }
                        }
                    } else {
                        currentTrial.result = 'false-alarm';
                        if (isPractice) {
                            setFeedbackMessage('❌ False Alarm');
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
                            nextTrial();
                        }, 500);
                    }
                }
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [phase, calibrationStep, currentTrial, keyPressed, trialStartTime, escapePressed, showEscapeConfirmation]);

    const startTrial = useCallback(() => {
        if (trialIndex < trials.length) {
            const trial = trials[trialIndex];
            setCurrentTrial(trial);
            setTrialStartTime(Date.now());
            setKeyPressed(false);
        }
    }, [trialIndex, trials]);

    const nextTrial = () => {
        setTrialIndex(prev => {
            const nextIndex = prev + 1;
            if (nextIndex >= trials.length) {
                if (isPractice) {
                    setPhase('practice-complete');
                } else {
                    setPhase('complete');
                }
                return prev;
            }
            return nextIndex;
        });
    };

    const startPractice = () => {
        setIsPractice(true);
        setTrials(generateTrials(CONFIG.PRACTICE_TRIALS, true));
        setTrialIndex(0);
        setPhase('practice');
    };

    const startMainTest = () => {
        setIsPractice(false);
        setTrials(generateTrials(CONFIG.MAIN_TEST_TRIALS));
        setTrialIndex(0);
        setPhase('main-test');
    };

    useEffect(() => {
        if ((phase === 'practice' || phase === 'main-test') && trials.length > 0) {
            startTrial();
        }
    }, [phase, trials, startTrial]);

    useEffect(() => {
        if (trialIndex < trials.length && (phase === 'practice' || phase === 'main-test')) {
            startTrial();
        }
    }, [trialIndex, phase, trials.length, startTrial]);

    const nextTrialCb = useCallback(() => {
        setTrialIndex(i => {
            const ni = i + 1;
            if (ni >= trials.length) {
                setPhase(isPractice ? 'practice-complete' : 'complete');
                return i;
            }
            return ni;
        });
    }, [isPractice, trials.length]);

    useEffect(() => {
        if ((phase === 'practice' || phase === 'main-test') && currentTrial?.type === 'nogo') {
            const timer = setTimeout(() => {
                setTrials(ts =>
                    ts.map(t =>
                        t.id === currentTrial.id ? { ...t, result: 'correct' } : t
                    )
                );

                if (isPractice) {
                    setFeedbackMessage('✅ Correct');
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
            }, CONFIG.NO_GO_DISPLAY_TIME);
            return () => clearTimeout(timer);
        }
    }, [currentTrial, isPractice, phase, nextTrialCb]);

    if (phase === 'instructions') {
        return (
            <div className={styles.container}>
                <div className={styles.modal}>
                    <h1>Go/No-Go Test Instructions</h1>
                    <div className={styles.instructions}>
                        <p><strong>You will see letters one at a time.</strong></p>
                        <ul>
                            <li>If you see any letter, symbol or number that is <strong>not X</strong> (Go), press the <strong>[spacebar]</strong> as quickly as you can.</li>
                            <li>If you see <strong>X</strong> (No-Go), withhold your response.</li>
                        </ul>
                        <p>There will be 100 trials, lasting about 2 minutes. You can practice 10 before beginning the test.</p>
                        <p className={styles.readyText}>Press <strong>[Enter]</strong> when you're ready to start the practice.</p>
                        <p className={styles.escapeTip}>Press <strong>[Escape]</strong> at any time to stop the process.</p>
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

    if (phase === 'calibration') {
        return (
            <div className={styles.container}>
                <div className={styles.calibrationGrid}>
                    {calibrationStep > 0 && calibrationStep <= 8 && (
                        <div
                            className={styles.calibrationDot}
                            style={{
                                left: `${calibrationDots[calibrationStep - 1].x}%`,
                                top: `${calibrationDots[calibrationStep - 1].y}%`
                            }}
                        />
                    )}
                </div>

                {calibrationStep === 0 && (
                    <div className={styles.calibrationInstructions}>
                        <h2>Calibration</h2>
                        <p>Look at each dot as it appears and press <strong>[Space]</strong> or <strong>[Enter]</strong> to continue to the next dot.</p>
                        <p>Press <strong>[Space]</strong> or <strong>[Enter]</strong> to start.</p>

                        <p>Tips: <ul>
                            <li>For best results, wait for the dot to pulse at least once before pressing <strong>[Space]</strong> or <strong>[Enter]</strong> to continue to the next dot.</li>
                            <li>Press <strong>[Escape]</strong> at any time to stop the process.</li>
                        </ul></p>
                    </div>
                )}

                {calibrationStep === 9 && (
                    <div className={styles.calibrationComplete}>
                        <h2>Calibration Complete</h2>
                        <div className={styles.calibrationButtons}>
                            <button onClick={startPractice} className={styles.button}>
                                Do a practice
                            </button>
                            <button onClick={startMainTest} className={styles.button}>
                                Proceed to main exam
                            </button>
                        </div>
                    </div>
                )}

                {calibrationStep > 0 && calibrationStep < 8 && (
                    <div className={styles.calibrationProgress}>
                        <p>Dot {calibrationStep} of 8</p>
                        <p>Press <strong>[Space]</strong> or <strong>[Enter]</strong> to continue</p>
                    </div>
                )}

                {calibrationStep === 8 && (
                    <div className={styles.calibrationProgress}>
                        <p>Press [Space] or [Enter] to complete calibration</p>
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

    if (phase === 'practice' || phase === 'main-test') {
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

    if (phase === 'complete') {
        const correctTrials = trials.filter(t => t.result === 'correct').length;
        const accuracy = (correctTrials / trials.length) * 100;

        return (
            <div className={styles.container}>
                <div className={styles.modal}>
                    <h1>Test Complete!</h1>
                    <div className={styles.results}>
                        <p>Accuracy: {accuracy.toFixed(1)}%</p>
                        <p>Correct responses: {correctTrials} / {trials.length}</p>
                    </div>
                    <button
                        onClick={() => window.location.href = '/results'}
                        className={styles.button}
                    >
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

    if (phase === 'practice-complete') {
        return (
            <div className={styles.container}>
                <div className={styles.modal}>
                    <h1>End of Practice</h1>
                    <div className={styles.instructions}>
                        <p>You have completed the practice trials.</p>
                        <p className={styles.readyText}>Press <strong>[Enter]</strong> to begin the real task.</p>
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
