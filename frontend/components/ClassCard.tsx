'use client';

import { useState } from 'react';
import styles from './ClassCard.module.css';
import { useRouter } from "next/navigation";
import router from 'next/router';
interface ClassCardProps {
  id: string;
  name: string;
  onView: (id: string) => void;
  onEdit: (id: string, newName: string) => void;
  onDelete: (id: string) => void;
}

export default function ClassCard({ id, name, onView, onEdit, onDelete }: ClassCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(name);
  const [isRemoving, setIsRemoving] = useState(false);
  const router = useRouter();
  const handleEdit = () => {
    setIsEditing(true);
    setEditName(name);
  };

  const handleSave = () => {
    if (editName.trim()) {
      onEdit(id, editName.trim());
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditName(name);
    setIsEditing(false);
  };



  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  };

  const handleDelete = () => {
    setIsRemoving(true);
    setTimeout(() => {
      onDelete(id);
    }, 300);
  };

  return (
    <div className={`${styles.card} ${isRemoving ? styles.cardRemoving : ''}`}>
      <div className={styles.cardHeader}>
        <div className={styles.cardTitle}>
          {isEditing ? (
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onBlur={handleSave}
              onKeyDown={handleKeyPress}
              className={styles.classNameInput}
              autoFocus
            />
          ) : (
            <h3 className={styles.className}>{name}</h3>
          )}
          
          <div className={styles.cardActions}>
            {!isEditing && (
              <>
                <button
                  onClick={handleEdit}
                  className={`${styles.actionButton} ${styles.editButton}`}
                  title="Edit class name"
                >
                  <svg className={styles.actionIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={handleDelete}
                  className={`${styles.actionButton} ${styles.deleteButton}`}
                  title="Delete class"
                >
                  <svg className={styles.actionIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      <div className={styles.placeholderImage}>
        <span>Class Image</span>
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
