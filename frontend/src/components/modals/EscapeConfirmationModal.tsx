import { FC } from 'react';
import styles from './EscapeConfirmationModal.module.css';

interface EscapeConfirmationModalProps {
    show: boolean;
    onCancel: () => void;
    onContinue: () => void;
}

const EscapeConfirmationModal: FC<EscapeConfirmationModalProps> = ({
    show,
    onCancel,
    onContinue
}) => {
    if (!show) return null;

    return (
        <div className={styles.escapeOverlay}>
            <div className={styles.escapeModal}>
                <h3>Stop Test?</h3>
                <p>Are you sure you want to stop the current process?</p>

                <div className={styles.buttonContainer}>
                    <button
                        className={`${styles.button} ${styles.cancelButton}`}
                        onClick={onCancel}
                    >
                        Yes, Cancel [Esc]
                    </button>
                    <button
                        className={`${styles.button} ${styles.continueButton}`}
                        onClick={onContinue}
                    >
                        No, Continue [Enter]
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EscapeConfirmationModal;
