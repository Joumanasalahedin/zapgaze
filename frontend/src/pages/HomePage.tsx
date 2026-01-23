import { FC, useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import styles from "./HomePage.module.css";

const HomePage: FC = () => {
  const [currentFactIndex, setCurrentFactIndex] = useState(0);
  const [greeting, setGreeting] = useState("");
  const [isManualControl, setIsManualControl] = useState(false);
  const autoResumeTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const adhdFacts = [
    {
      fact: "ADHD affects approximately 5-7% of children and 2-5% of adults worldwide, making it one of the most common neurodevelopmental disorders.",
      source: "World Health Organization (WHO)",
      image: "/images/doctor-testing-patient-eyesight.jpg",
    },
    {
      fact: "Research shows that people with ADHD often have differences in brain structure and function, particularly in areas responsible for attention, impulse control, and executive function.",
      source: "National Institute of Mental Health (NIMH)",
      image: "/images/eye-tracking-webcam.jpg",
    },
    {
      fact: "Contrary to popular belief, ADHD is not caused by poor parenting, too much sugar, or watching too much TV. It's a complex neurobiological condition with strong genetic components.",
      source: "American Academy of Pediatrics",
      image: "/images/front-view-girl-getting-her-eyes-checked.jpg",
    },
    {
      fact: "Many successful people have ADHD, including entrepreneurs, artists, and athletes. The condition can bring creativity, hyperfocus, and unique problem-solving abilities.",
      source: "CHADD (Children and Adults with Attention-Deficit/Hyperactivity Disorder)",
      image: "/images/ophthalmologist-doctor-consulting-patient.jpg",
    },
    {
      fact: "Early diagnosis and treatment of ADHD can significantly improve academic performance, social relationships, and overall quality of life for both children and adults.",
      source: "Centers for Disease Control and Prevention (CDC)",
      image: "/images/lab-eye-openness.png",
    },
  ];

  useEffect(() => {
    const hour = new Date().getHours();
    let timeGreeting = "";

    if (hour < 12) {
      timeGreeting = "Good morning";
    } else if (hour < 17) {
      timeGreeting = "Good afternoon";
    } else {
      timeGreeting = "Good evening";
    }

    setGreeting(timeGreeting);
  }, []);

  useEffect(() => {
    if (isManualControl) return;

    const interval = setInterval(() => {
      setCurrentFactIndex((prevIndex) => (prevIndex === adhdFacts.length - 1 ? 0 : prevIndex + 1));
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
    setCurrentFactIndex((prevIndex) => (prevIndex === 0 ? adhdFacts.length - 1 : prevIndex - 1));
  };

  const goToNext = () => {
    setIsManualControl(true);
    setCurrentFactIndex((prevIndex) => (prevIndex === adhdFacts.length - 1 ? 0 : prevIndex + 1));
  };

  const goToFact = (index: number) => {
    setIsManualControl(true);
    setCurrentFactIndex(index);
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
    <div className={styles.homeContainer}>
      <div className={styles.heroSection}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>{greeting}!</h1>
          <p className={styles.heroSubtitle}>
            Welcome to zapgaze™ — A revolutionary ADHD evaluation tool through advanced pupillometry
            technology
          </p>
          <div className={styles.heroAction}>
            <Link to="/test" className={styles.primaryButton}>
              Take the Test
            </Link>
          </div>
        </div>
      </div>

      <div className={styles.factsSection}>
        <div className={styles.factsCard}>
          <div className={styles.factsHeader}>
            <h2 className={styles.sectionTitle}>Did You Know?</h2>
            <p className={styles.sectionSubtitle}>
              Discover fascinating facts about ADHD and its impact on daily life
            </p>
          </div>

          <div className={styles.factContent}>
            <div className={styles.factTextSection}>
              <div className={styles.factQuote}>
                <p className={styles.factText}>"{adhdFacts[currentFactIndex].fact}"</p>
                <p className={styles.factSource}>— {adhdFacts[currentFactIndex].source}</p>
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
                  className={
                    index === currentFactIndex ? `${styles.dot} ${styles.dotActive}` : styles.dot
                  }
                  onClick={() => goToFact(index)}
                />
              ))}
            </div>
            <button onClick={goToNext} className={styles.navButton}>
              Next &gt;
            </button>
          </div>
        </div>
      </div>

      <div className={styles.aboutSection}>
        <div className={styles.aboutCard}>
          <div className={styles.aboutContent}>
            <h2 className={styles.sectionTitle}>About zapgaze™</h2>
            <p className={styles.sectionText}>
              zapgaze™ uses cutting-edge pupillometry technology to evaluate potential ADHD
              indicators through precise eye movement and pupil response analysis. Our non-invasive,
              scientifically-backed approach provides quick and accurate assessments that can help
              identify attention-related challenges early.
            </p>
            <div className={styles.aboutFeatures}>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🔬</span>
                <span className={styles.featureText}>Scientifically Validated</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>⚡</span>
                <span className={styles.featureText}>Quick & Non-Invasive</span>
              </div>
              <div className={styles.featureItem}>
                <span className={styles.featureIcon}>🎯</span>
                <span className={styles.featureText}>High Accuracy</span>
              </div>
            </div>
            <Link to="/about" className={styles.secondaryButton}>
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
