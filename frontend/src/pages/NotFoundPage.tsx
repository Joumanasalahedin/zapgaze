import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styles from './NotFoundPage.module.css';
import Lottie from 'lottie-react';

const NotFoundPage: React.FC = () => {
    const [animationData, setAnimationData] = useState(null);

    useEffect(() => {
        fetch('/lottie/alert-lottie.json')
            .then(response => response.json())
            .then(data => setAnimationData(data))
            .catch(error => console.error('Error loading Lottie animation:', error));
    }, []);

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.lottieContainer}>
                    {animationData ? (
                        <Lottie
                            animationData={animationData}
                            loop={true}
                            className={styles.lottie}
                        />
                    ) : (
                        <div className={styles.lottiePlaceholder}>
                            :(
                        </div>
                    )}
                </div>

                <h1 className={styles.title}>
                    404
                </h1>

                <h2 className={styles.subtitle}>
                    Page Not Found
                </h2>

                <p className={styles.description}>
                    The page you're looking for doesn't exist.
                </p>

                <Link
                    to="/"
                    className={styles.button}
                >
                    Back to Home
                </Link>
            </div>
        </div>
    );
};

export default NotFoundPage;
