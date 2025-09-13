'use client';

import { useState } from 'react';
import styles from './page.module.css';

export default function ClassDetailPage() {
  const [restrictions, setRestrictions] = useState('');
  const [teachingStyle, setTeachingStyle] = useState('');
  const [studentAge, setStudentAge] = useState('');
  const [subject, setSubject] = useState('');
  const [otherNotes, setOtherNotes] = useState('');

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      // Handle file upload logic here
      console.log('Files uploaded:', files);
    }
  };

  return (
    <div className={styles.contentGrid}>
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Restrictions</h2>
        <textarea
          className={styles.textArea}
          placeholder="Enter any restrictions or guidelines for the class..."
          value={restrictions}
          onChange={(e) => setRestrictions(e.target.value)}
        />
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Teaching Style</h2>
        <textarea
          className={styles.textArea}
          placeholder="Describe your teaching style and approach..."
          value={teachingStyle}
          onChange={(e) => setTeachingStyle(e.target.value)}
        />
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Resources</h2>
        <div className={styles.uploadArea} onClick={() => document.getElementById('fileInput')?.click()}>
          <svg className={styles.uploadIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <div className={styles.uploadText}>Upload resources</div>
          <div className={styles.uploadSubtext}>Click to select files or drag and drop</div>
        </div>
        <input
          id="fileInput"
          type="file"
          multiple
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />
      </div>

      <div className={styles.rightColumn}>
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Class Information</h2>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="studentAge">Student age</label>
            <input
              id="studentAge"
              className={styles.input}
              type="text"
              placeholder="e.g., 12-14 years old"
              value={studentAge}
              onChange={(e) => setStudentAge(e.target.value)}
            />
          </div>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="subject">Subject</label>
            <input
              id="subject"
              className={styles.input}
              type="text"
              placeholder="e.g., Mathematics, Science"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="otherNotes">Other notes</label>
            <textarea
              id="otherNotes"
              className={styles.smallTextArea}
              placeholder="Any additional information..."
              value={otherNotes}
              onChange={(e) => setOtherNotes(e.target.value)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
