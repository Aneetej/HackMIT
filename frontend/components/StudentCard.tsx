'use client';

import styles from './StudentCard.module.css';

interface StudentCardProps {
  id: string;
  name: string;
  onView: (id: string) => void;
}

export default function StudentCard({ id, name, onView }: StudentCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.studentName}>{name}</h3>
      </div>

      <div className={styles.placeholderImage}>
      </div>

      <div className={styles.cardFooter}>
        <button
          onClick={() => onView(id)}
          className={styles.viewButton}
        >
          View
        </button>
      </div>
    </div>
  );
}
