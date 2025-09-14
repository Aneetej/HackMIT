'use client';

import { useState } from 'react';
import StudentClassCard from './StudentClassCard';
import styles from './StudentSidebar.module.css';

interface Class {
  id: string;
  name: string;
}

interface StudentSidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  classes: Class[];
  selectedClass: string | null;
  onSelectClass: (classId: string) => void;
  joinCode: string;
  setJoinCode: (code: string) => void;
  onJoinClass: () => void;
  interests: string;
  setInterests: (interests: string) => void;
  learningStyle: string;
  setLearningStyle: (style: string) => void;
  onUpdatePreferences: () => void;
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
  isLoading?: boolean;
  error?: string | null;
}

export default function StudentSidebar({
  activeTab,
  setActiveTab,
  classes,
  selectedClass,
  onSelectClass,
  joinCode,
  setJoinCode,
  onJoinClass,
  interests,
  setInterests,
  learningStyle,
  setLearningStyle,
  onUpdatePreferences,
  sidebarCollapsed,
  onToggleSidebar,
  isLoading,
  error
}: StudentSidebarProps) {
  return (
    <div className={`${styles.leftSidebar} ${sidebarCollapsed ? styles.sidebarCollapsed : ''}`}>
      <button className={styles.collapseButton} onClick={onToggleSidebar}>
        {sidebarCollapsed ? '→' : '←'}
      </button>
      <div className={styles.tabNavigation}>
        <button 
          className={`${styles.tab} ${activeTab === 'Classes' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('Classes')}
        >
          Classes
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'Preferences' ? styles.tabActive : ''}`}
          onClick={() => setActiveTab('Preferences')}
        >
          Preferences
        </button>
      </div>

      {activeTab === 'Classes' && (
        <>
          <div className={styles.joinSection}>
            <div className={styles.joinCard}>
              <div className={styles.joinHeader}>
                <span className={styles.joinTitle}>Join Class</span>
              </div>
              {error && (
                <div className={styles.errorMessage}>
                  {error}
                </div>
              )}
              <input
                type="text"
                className={styles.joinInput}
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
                placeholder="Enter class ID"
              />
              <button 
                className={styles.joinButton}
                onClick={onJoinClass}
              >
                Join
              </button>
            </div>
          </div>
          
          <div className={styles.classesSection}>
            {classes.map((classItem) => (
              <StudentClassCard
                key={classItem.id}
                id={classItem.id}
                name={classItem.name}
                isSelected={selectedClass === classItem.id}
                onSelect={onSelectClass}
              />
            ))}
          </div>
        </>
      )}

      {activeTab === 'Preferences' && (
        <div className={styles.preferencesSection}>
          <div className={styles.preferenceCard}>
            <h3 className={styles.preferenceTitle}>Describe your interests</h3>
            <textarea
              className={styles.preferenceTextarea}
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              onBlur={onUpdatePreferences}
              placeholder=""
            />
          </div>
          
          <div className={styles.preferenceCard}>
            <h3 className={styles.preferenceTitle}>Describe how you like to learn</h3>
            <textarea
              className={styles.preferenceTextarea}
              value={learningStyle}
              onChange={(e) => setLearningStyle(e.target.value)}
              onBlur={onUpdatePreferences}
              placeholder=""
            />
          </div>
        </div>
      )}
    </div>
  );
}
