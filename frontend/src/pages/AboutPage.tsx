import { FC } from "react";
import styles from "./AboutPage.module.css";
import { Link } from "react-router-dom";

const AboutPage: FC = () => {
  return (
    <div className={styles.aboutContainer}>
      <div className={styles.heroSection}>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>About zapgaze™</h1>
          <p className={styles.heroSubtitle}>
            Revolutionizing eye tracking technology for accessible, accurate, and affordable vision
            assessment
          </p>
        </div>
      </div>

      <div className={styles.contentSection}>
        <div className={styles.missionCard}>
          <h2 className={styles.sectionTitle}>Our Mission</h2>
          <p className={styles.sectionText}>
            At zapgaze, we believe that advanced eye tracking technology should be accessible to
            everyone. Our platform combines cutting-edge computer vision algorithms with
            user-friendly interfaces to provide accurate eye tracking and vision assessment tools
            that work with standard webcams.
          </p>
        </div>

        <div className={styles.featuresGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔬</div>
            <h3 className={styles.featureTitle}>Advanced Technology</h3>
            <p className={styles.featureText}>
              Powered by state-of-the-art computer vision and machine learning algorithms that
              deliver precise eye tracking results.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>💻</div>
            <h3 className={styles.featureTitle}>Webcam Compatible</h3>
            <p className={styles.featureText}>
              No expensive hardware required. Our solution works with standard webcams found in most
              computers and laptops.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🎯</div>
            <h3 className={styles.featureTitle}>High Accuracy</h3>
            <p className={styles.featureText}>
              Achieve professional-grade eye tracking accuracy through our advanced calibration and
              tracking algorithms.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🌐</div>
            <h3 className={styles.featureTitle}>Web-Based</h3>
            <p className={styles.featureText}>
              Access our platform from any device with a modern web browser. No downloads or
              installations required.
            </p>
          </div>
        </div>

        <div className={styles.technologySection}>
          <h2 className={styles.sectionTitle}>Technology Stack</h2>
          <div className={styles.techGrid}>
            <div className={styles.techItem}>
              <h4 className={styles.techTitle}>Frontend</h4>
              <p className={styles.techDescription}>
                React, TypeScript, and modern CSS for responsive design
              </p>
            </div>
            <div className={styles.techItem}>
              <h4 className={styles.techTitle}>Backend</h4>
              <p className={styles.techDescription}>
                Python FastAPI with real-time WebSocket communication
              </p>
            </div>
            <div className={styles.techItem}>
              <h4 className={styles.techTitle}>Eye Tracking</h4>
              <p className={styles.techDescription}>
                MediaPipe, PyGaze, and custom computer vision algorithms
              </p>
            </div>
            <div className={styles.techItem}>
              <h4 className={styles.techTitle}>Database</h4>
              <p className={styles.techDescription}>
                SQLite with SQLAlchemy ORM for data persistence
              </p>
            </div>
          </div>
        </div>

        <div className={styles.applicationsSection}>
          <h2 className={styles.sectionTitle}>Applications</h2>
          <div className={styles.applicationsList}>
            <div className={styles.applicationItem}>
              <h4 className={styles.applicationTitle}>Vision Research</h4>
              <p className={styles.applicationText}>
                Conduct eye tracking studies for academic and commercial research purposes
              </p>
            </div>
            <div className={styles.applicationItem}>
              <h4 className={styles.applicationTitle}>Accessibility Testing</h4>
              <p className={styles.applicationText}>
                Evaluate website usability and accessibility through eye tracking analysis
              </p>
            </div>
            <div className={styles.applicationItem}>
              <h4 className={styles.applicationTitle}>User Experience</h4>
              <p className={styles.applicationText}>
                Understand user behavior and optimize interfaces based on gaze patterns
              </p>
            </div>
            <div className={styles.applicationItem}>
              <h4 className={styles.applicationTitle}>Medical Screening</h4>
              <p className={styles.applicationText}>
                Assist in preliminary vision assessment and eye movement analysis
              </p>
            </div>
          </div>
        </div>

        <div className={styles.contactSection}>
          <h2 className={styles.sectionTitle}>Get Started</h2>
          <p className={styles.contactText}>
            Ready to experience the future of eye tracking? Try our demo or contact us to learn more
            about integrating zapgaze into your projects.
          </p>
          <div className={styles.contactButtons}>
            <Link to="/test" className={styles.primaryButton}>
              Try Demo
            </Link>
            <button
              onClick={() => (window.location.href = "mailto:somtochukwu.mbuko@stud.th-deg.de")}
              className={styles.secondaryButton}
            >
              Contact Us
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
