import { FC } from "react";
import { Link, useLocation } from "react-router-dom";
import styles from "./Header.module.css";
import GenericIcon from "./GenericIcon";

const Header: FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className={styles.header}>
      <div className={styles.headerInner}>
        <div className="flex-shrink-0">
          <Link to="/" className={styles.logo}>
            zapgaze&trade;
          </Link>
        </div>

        <nav className={styles.nav}>
          <Link to="/" className={`${styles.link} ${isActive("/") ? styles.linkActive : ""}`}>
            Home
          </Link>
          <Link
            to="/test"
            className={`${styles.link} ${isActive("/test") ? styles.linkActive : ""}`}
          >
            Test
          </Link>
          <Link
            to="/results"
            className={`${styles.link} ${isActive("/results") ? styles.linkActive : ""}`}
          >
            Results
          </Link>
          <Link
            to="/about"
            className={`${styles.link} ${isActive("/about") ? styles.linkActive : ""}`}
          >
            About
          </Link>
        </nav>

        <GenericIcon
          icon="github"
          onClick={() => window.open("https://github.com/Joumanasalahedin/zapgaze", "_blank")}
          onHoverStyle={{ color: "var(--primary-color)" }}
        />
      </div>
    </header>
  );
};

export default Header;
