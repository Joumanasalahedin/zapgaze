import { FC } from "react";
import styles from "./Footer.module.css";

const Footer: FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className={styles.footer}>
      <div className={styles.footerInner}>
        <div className={styles.left}>
          <span className={styles.bold600}>zapgaze&trade;</span> &copy; {currentYear} All rights
          reserved
        </div>
        <div className={styles.right}>
          Designed by <span className={styles.bold500}>Joumana</span> and{" "}
          <span className={styles.bold500}>Somto</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
