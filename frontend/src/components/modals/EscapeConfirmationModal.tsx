import React from 'react';
import styles from './EscapeConfirmationModal.module.css';

interface EscapeConfirmationModalProps {
    show: boolean;
    countdown: number;
}

const EscapeConfirmationModal: React.FC<EscapeConfirmationModalProps> = ({ show, countdown }) => {
    if (!show) return null;

    return (
        <div className={styles.escapeOverlay}>
            <div className={styles.escapeModal}>
                <h3>Stop Test?</h3>
                <p>Press <b>[Escape]</b> again within {countdown} seconds to stop the current process. Press <b>[Enter]</b> to resume process.</p>
            </div>
        </div>
    );
};

export default EscapeConfirmationModal;
