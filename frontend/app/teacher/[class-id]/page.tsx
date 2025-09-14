'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { teacherApi } from '../../../lib/teacher/apis';
import styles from './page.module.css';

export default function ClassDetailPage() {
  const params = useParams();
  const classId = params['class-id'] as string;
  
  const [restrictions, setRestrictions] = useState('');
  const [teachingStyle, setTeachingStyle] = useState('');
  const [studentGrade, setStudentGrade] = useState('');
  const [subject, setSubject] = useState('');
  const [otherNotes, setOtherNotes] = useState('');
  
  // Track original values for change detection
  const [originalRestrictions, setOriginalRestrictions] = useState('');
  const [originalTeachingStyle, setOriginalTeachingStyle] = useState('');
  const [originalStudentGrade, setOriginalStudentGrade] = useState('');
  const [originalSubject, setOriginalSubject] = useState('');
  const [originalOtherNotes, setOriginalOtherNotes] = useState('');
  
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadClassData();
  }, [classId]);

  const loadClassData = async () => {
    // For now, we'll initialize with empty values since we don't have a get single class endpoint
    // In a real app, you'd fetch the class data here
    setIsLoading(false);
  };

  useEffect(() => {
    const fetchClassData = async () => {
      try {
        const classData = await teacherApi.getClass(classId);
        if (classData.success) {
          setRestrictions(classData.class.restrictions || '');
          setTeachingStyle(classData.class.teachingStyle || '');
          setStudentGrade(classData.class.studentGrade || '');
          setSubject(classData.class.subject || '');
          setOtherNotes(classData.class.otherNotes || '');
          setOriginalRestrictions(classData.class.restrictions || '');
          setOriginalTeachingStyle(classData.class.teachingStyle || '');
          setOriginalStudentGrade(classData.class.studentGrade || '');
          setOriginalSubject(classData.class.subject || '');
          setOriginalOtherNotes(classData.class.otherNotes || '');
        }
      } catch (error) {
        console.error('Error fetching class data:', error);
      }
    };

    if (classId) {
      fetchClassData();
    }
  }, [classId]);

  const updateClassField = async (field: 'restrictions' | 'teachingStyle' | 'studentGrade' | 'subject' | 'otherNotes', value: string, originalValue: string) => {
    if (value === originalValue) return; // No change, don't update
    
    try {
      const updateData = { [field]: value };
      await teacherApi.updateClass(classId, updateData);
      
      // Update the original value to the new value
      if (field === 'restrictions') {
        setOriginalRestrictions(value);
      } else if (field === 'teachingStyle') {
        setOriginalTeachingStyle(value);
      } else if (field === 'studentGrade') {
        setOriginalStudentGrade(value);
      } else if (field === 'subject') {
        setOriginalSubject(value);
      } else if (field === 'otherNotes') {
        setOriginalOtherNotes(value);
      }
    } catch (error) {
      console.error(`Error updating ${field}:`, error);
    }
  };

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
          onBlur={() => updateClassField('restrictions', restrictions, originalRestrictions)}
        />
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Teaching Style</h2>
        <textarea
          className={styles.textArea}
          placeholder="Describe your teaching style and approach..."
          value={teachingStyle}
          onChange={(e) => setTeachingStyle(e.target.value)}
          onBlur={() => updateClassField('teachingStyle', teachingStyle, originalTeachingStyle)}
        />
      </div>


      <div className={styles.rightColumn}>
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Student Grade Level</h2>
          <input
            className={styles.input}
            type="text"
            placeholder="Enter student grade level..."
            value={studentGrade}
            onChange={(e) => setStudentGrade(e.target.value)}
            onBlur={() => updateClassField('studentGrade', studentGrade, originalStudentGrade)}
          />
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Subject</h2>
          <input
            className={styles.input}
            type="text"
            placeholder="Enter subject..."
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            onBlur={() => updateClassField('subject', subject, originalSubject)}
          />
        </div>

        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Other notes</h2>
          <textarea
            className={styles.textArea}
            placeholder="Any other notes..."
            value={otherNotes}
            onChange={(e) => setOtherNotes(e.target.value)}
            onBlur={() => updateClassField('otherNotes', otherNotes, originalOtherNotes)}
          />
        </div>
      </div>
    </div>
  );
}
