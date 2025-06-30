import React, { FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './IntakeQuestionnairePage.module.css';

export const ASRS_QUESTIONS = [
    {
        id: 1,
        text: 'How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?',
    },
    {
        id: 2,
        text: 'How often do you leave your seat in meetings or other situations in which you are expected to remain seated?',
    },
    {
        id: 3,
        text: 'How often do you have difficulty unwinding and relaxing when you have time to yourself?',
    },
    {
        id: 4,
        text: "When you're in a conversation, how often do you find yourself finishing the sentences of the people you are talking to before they can finish them themselves?",
    },
    {
        id: 5,
        text: 'How often do you put things off until the last minute?',
    },
    {
        id: 6,
        text: 'How often do you depend on others to keep your life in order and attend to details?',
    },
];

export const ASRS_OPTIONS = [
    'Never',
    'Rarely',
    'Sometimes',
    'Often',
    'Very Often',
];

const SCORE_MAP = [0, 1, 2, 3, 4];

const IntakeQuestionnairePage: FC = () => {
    const [answers, setAnswers] = useState<(number | null)[]>(Array(ASRS_QUESTIONS.length).fill(null));
    const [touched, setTouched] = useState(false);
    const [name, setName] = useState('');
    const [birthdate, setBirthdate] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (qIdx: number, optIdx: number) => {
        setAnswers(prev => {
            const next = [...prev];
            next[qIdx] = optIdx;
            return next;
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setTouched(true);
        if (!name.trim() || !birthdate.trim() || answers.some(a => a === null)) {
            return;
        }
        setLoading(true);
        try {
            const scoredAnswers = answers.map(idx => SCORE_MAP[idx as number]);
            const payload = {
                name,
                birthdate,
                answers: scoredAnswers,
            };
            const res = await fetch('http://localhost:8000/intake/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error('Failed to submit intake.');
            const data = await res.json();
            const intakeDataWithTimestamp = {
                ...payload,
                ...data,
                timestamp: Date.now()
            };
            localStorage.setItem('asrs5-intake', JSON.stringify(intakeDataWithTimestamp));
            navigate('/test');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form className={styles.questionnaire} onSubmit={handleSubmit}>
            <h2 className={styles.title}>ASRS-5 Online Assessment</h2>
            <div className={styles.userFields}>
                <label className={`${styles.userLabel} ${styles.width50}`}>
                    Name
                    <input
                        type="text"
                        className={styles.userInput}
                        value={name}
                        onChange={e => setName(e.target.value)}
                        required
                        placeholder="Your name"
                    />
                </label>
                <label className={styles.userLabel}>
                    Birthdate
                    <input
                        type="date"
                        className={styles.userInput}
                        value={birthdate}
                        onChange={e => setBirthdate(e.target.value)}
                        required
                    />
                </label>
            </div>
            {ASRS_QUESTIONS.map((q, qIdx) => (
                <div key={q.id} className={styles.questionBlock}>
                    <div className={styles.questionText}>
                        <span className={styles.questionLabel}>Question {qIdx + 1}:</span> {q.text}
                    </div>
                    <div className={styles.optionsRow}>
                        {ASRS_OPTIONS.map((opt, optIdx) => (
                            <label key={opt} className={styles.optionLabel}>
                                <input
                                    type="radio"
                                    name={`q${q.id}`}
                                    value={optIdx}
                                    checked={answers[qIdx] === optIdx}
                                    onChange={() => handleChange(qIdx, optIdx)}
                                    className={styles.radio}
                                />
                                <span className={styles.optionText}>{opt}</span>
                            </label>
                        ))}
                    </div>
                </div>
            ))}
            {touched && (answers.some(a => a === null) || !name.trim() || !birthdate.trim()) && (
                <div className={styles.errorMsg}>Please fill out all fields and answer all questions before continuing.</div>
            )}
            <button type="submit" className={styles.submitBtn} disabled={loading}>
                {loading ? 'Submitting...' : 'Submit'}
            </button>
        </form>
    );
};

export default IntakeQuestionnairePage;
