'use client';

import styles from './ClassCard.module.css';

interface AddClassCardProps {
  onAddClass: () => void;
}

export default function AddClassCard({ onAddClass }: AddClassCardProps) {
  return (
    <div className={styles.addCard} onClick={onAddClass}>
      <div className={styles.addCardContent}>
        <div className={styles.addIconContainer}>
          <svg 
            className={styles.addIcon} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </div>
        <h3 className={styles.addTitle}>
          Add Class
        </h3>
      </div>
    </div>
  );
}
