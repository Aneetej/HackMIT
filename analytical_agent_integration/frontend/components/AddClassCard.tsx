'use client';

import { useState } from 'react';
import styles from './ClassCard.module.css';

interface AddClassCardProps {
  onCreateClass: (className: string) => void;
}

export default function AddClassCard({ onCreateClass }: AddClassCardProps) {
  const [className, setClassName] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (className.trim()) {
      setIsCreating(true);
      await onCreateClass(className.trim());
      setClassName('');
      setIsCreating(false);
    }
  };

  return (
    <div className={styles.addCard}>
      <div className={styles.addCardContent}>
        <h3 className={styles.addTitle}>Create New Class</h3>
        <form onSubmit={handleSubmit} className={styles.createForm}>
          <input
            type="text"
            value={className}
            onChange={(e) => setClassName(e.target.value)}
            placeholder="Enter class title..."
            className={styles.classInput}
            disabled={isCreating}
            maxLength={50}
          />
          <button
            type="submit"
            disabled={!className.trim() || isCreating}
            className={styles.createButton}
          >
            {isCreating ? 'Creating...' : 'Create Class'}
          </button>
        </form>
      </div>
    </div>
  );
}
