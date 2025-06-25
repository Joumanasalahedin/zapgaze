import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import styles from './HomePage.module.css';

const HomePage: React.FC = () => {
    const [currentFactIndex, setCurrentFactIndex] = useState(0);
    const [greeting, setGreeting] = useState('');
    const [isManualControl, setIsManualControl] = useState(false);
    const autoResumeTimeoutRef = useRef<number | null>(null);

    const adhdFacts = [
        {
            fact: "ADHD affects approximately 5-7% of children and 2-5% of adults worldwide, making it one of the most common neurodevelopmental disorders.",
            source: "World Health Organization (WHO)",
            image: "../public/images/doctor-testing-patient-eyesight.jpg"
        },
        {
            fact: "Research shows that people with ADHD often have differences in brain structure and function, particularly in areas responsible for attention, impulse control, and executive function.",
            source: "National Institute of Mental Health (NIMH)",
            image: "../public/images/eye-tracking-webcam.jpg"
        },
        {
            fact: "Contrary to popular belief, ADHD is not caused by poor parenting, too much sugar, or watching too much TV. It's a complex neurobiological condition with strong genetic components.",
            source: "American Academy of Pediatrics",
            image: "../public/images/front-view-girl-getting-her-eyes-checked.jpg"
        },
        {
            fact: "Many successful people have ADHD, including entrepreneurs, artists, and athletes. The condition can bring creativity, hyperfocus, and unique problem-solving abilities.",
            source: "CHADD (Children and Adults with Attention-Deficit/Hyperactivity Disorder)",
            image: "../public/images/ophthalmologist-doctor-consulting-patient.jpg"
        },
        {
            fact: "Early diagnosis and treatment of ADHD can significantly improve academic performance, social relationships, and overall quality of life for both children and adults.",
            source: "Centers for Disease Control and Prevention (CDC)",
            image: "../public/images/pupil-as-window-of-the-eye.jpg"
        }
    ];

    useEffect(() => {
        const hour = new Date().getHours();
        let timeGreeting = '';

        if (hour < 12) {
            timeGreeting = 'Good morning';
        } else if (hour < 17) {
            timeGreeting = 'Good afternoon';
        } else {
            timeGreeting = 'Good evening';
        }

        setGreeting(timeGreeting);
    }, []);

    useEffect(() => {
        if (isManualControl) return;

        const interval = setInterval(() => {
            setCurrentFactIndex((prevIndex) =>
                prevIndex === adhdFacts.length - 1 ? 0 : prevIndex + 1
            );
        }, 10000);

        return () => clearInterval(interval);
    }, [adhdFacts.length, isManualControl]);

    const clearAutoResumeTimeout = () => {
        if (autoResumeTimeoutRef.current) {
            clearTimeout(autoResumeTimeoutRef.current);
            autoResumeTimeoutRef.current = null;
        }
    };

    const startAutoResumeTimer = () => {
        clearAutoResumeTimeout();
        autoResumeTimeoutRef.current = setTimeout(() => {
            setIsManualControl(false);
        }, 5000);
    };

    const goToPrevious = () => {
        setIsManualControl(true);
        setCurrentFactIndex((prevIndex) =>
            prevIndex === 0 ? adhdFacts.length - 1 : prevIndex - 1
        );
    };

    const goToNext = () => {
        setIsManualControl(true);
        setCurrentFactIndex((prevIndex) =>
            prevIndex === adhdFacts.length - 1 ? 0 : prevIndex + 1
        );
    };

    const handleNavigationMouseEnter = () => {
        clearAutoResumeTimeout();
    };

    const handleNavigationMouseLeave = () => {
        if (isManualControl) {
            startAutoResumeTimer();
        }
    };

    useEffect(() => {
        return () => {
            clearAutoResumeTimeout();
        };
    }, []);

    return (
        <div className="container">
            <div className={styles.greeting}>
                <h1 className={styles.greetingTitle}>
                    {greeting}!
                </h1>
                <p className={styles.greetingSubtitle}>
                    Welcome to zapgaze&trade; &mdash; A revolutionary ADHD detection tool through advanced pupillometry technology
                </p>
            </div>

            <div className={styles.action}>
                <Link to="/test" className={`${styles.actionLink} btn-primary`}>
                    Take the Test
                </Link>
            </div>

            <div className={styles.factCard}>
                <div className={styles.factContainer}>
                    <div className={styles.factTextContainer}>
                        <div className={styles.factTitle}>Did You Know?</div>
                        <div className={styles.factContent}>
                            <div className={styles.factTextSection}>
                                <p className={styles.factText}>
                                    "{adhdFacts[currentFactIndex].fact}"
                                </p>
                                <p className={styles.factSource}>
                                    — {adhdFacts[currentFactIndex].source}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className={styles.factImageSection}>
                        <img
                            src={adhdFacts[currentFactIndex].image}
                            alt="ADHD Fact Illustration"
                            className={styles.factImage}
                        />
                    </div>
                </div>

                <div
                    className={styles.navigationControls}
                    onMouseEnter={handleNavigationMouseEnter}
                    onMouseLeave={handleNavigationMouseLeave}
                >
                    <button onClick={goToPrevious} className={styles.navButton}>
                        &lt; Previous
                    </button>
                    <div className={styles.factDots}>
                        {adhdFacts.map((_, index) => (
                            <div
                                key={index}
                                className={index === currentFactIndex ? `${styles.dot} ${styles.dotActive}` : styles.dot}
                            />
                        ))}
                    </div>
                    <button onClick={goToNext} className={styles.navButton}>
                        Next &gt;
                    </button>
                </div>
            </div>

            <div className={styles.overviewCard}>
                <div className={styles.overviewTitle}>About zapgaze&trade;</div>
                <p className={styles.overviewText}>
                    zapgaze&trade; uses cutting-edge pupillometry technology to detect potential ADHD indicators
                    through precise eye movement and pupil response analysis. Our non-invasive,
                    scientifically-backed approach provides quick and accurate assessments that can help
                    identify attention-related challenges early.
                </p>
                <Link to="/about" className="btn-secondary">
                    Learn More
                </Link>
            </div>
        </div>
    );
};

export default HomePage; 