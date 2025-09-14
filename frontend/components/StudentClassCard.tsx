'use client';

import { useState } from 'react';
import styles from './StudentClassCard.module.css';

interface StudentClassCardProps {
  id: string;
  name: string;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

export default function StudentClassCard({ id, name, isSelected, onSelect }: StudentClassCardProps) {
  return (
    <div 
      className={`${styles.classCard} ${isSelected ? styles.classCardSelected : ''}`}
      onClick={() => onSelect(id)}
    >
      <div className={styles.classHeader}>
        <span className={styles.className}>{name}</span>
      </div>
      <div className={styles.classImage}>

      </div>

    </div>
  );
}
