import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './HomePage.module.css';

const HomePage: React.FC = () => {
    const [currentFactIndex, setCurrentFactIndex] = useState(0);
    const [greeting, setGreeting] = useState('');

    const adhdFacts = [
        {
            fact: "ADHD affects approximately 5-7% of children and 2-5% of adults worldwide, making it one of the most common neurodevelopmental disorders.",
            source: "World Health Organization (WHO)"
        },
        {
            fact: "Research shows that people with ADHD often have differences in brain structure and function, particularly in areas responsible for attention, impulse control, and executive function.",
            source: "National Institute of Mental Health (NIMH)"
        },
        {
            fact: "Contrary to popular belief, ADHD is not caused by poor parenting, too much sugar, or watching too much TV. It's a complex neurobiological condition with strong genetic components.",
            source: "American Academy of Pediatrics"
        },
        {
            fact: "Many successful people have ADHD, including entrepreneurs, artists, and athletes. The condition can bring creativity, hyperfocus, and unique problem-solving abilities.",
            source: "CHADD (Children and Adults with Attention-Deficit/Hyperactivity Disorder)"
        },
        {
            fact: "Early diagnosis and treatment of ADHD can significantly improve academic performance, social relationships, and overall quality of life for both children and adults.",
            source: "Centers for Disease Control and Prevention (CDC)"
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
        const interval = setInterval(() => {
            setCurrentFactIndex((prevIndex) =>
                prevIndex === adhdFacts.length - 1 ? 0 : prevIndex + 1
            );
        }, 5000);

        return () => clearInterval(interval);
    }, [adhdFacts.length]);

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
                <div className={styles.factTitle}>Did You Know?</div>
                <div>
                    <p className={styles.factText}>
                        "{adhdFacts[currentFactIndex].fact}"
                    </p>
                    <p className={styles.factSource}>
                        — {adhdFacts[currentFactIndex].source}
                    </p>
                </div>
                <div className={styles.factDots}>
                    {adhdFacts.map((_, index) => (
                        <div
                            key={index}
                            className={index === currentFactIndex ? `${styles.dot} ${styles.dotActive}` : styles.dot}
                        />
                    ))}
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