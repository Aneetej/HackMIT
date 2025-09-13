'use client';

import { useState } from 'react';
import Navigation from '../../components/Navigation';
import ClassCard from '../../components/ClassCard';
import AddClassCard from '../../components/AddClassCard';
import styles from './page.module.css';
import { v4 as uuidv4 } from 'uuid';
import { useRouter } from 'next/navigation';
interface ClassData {
  id: string;
  name: string;
}

export default function TeacherDashboard() {
  const [classes, setClasses] = useState<ClassData[]>([
    { id: '1', name: 'Mathematics 101' },
    { id: '2', name: 'Physics Fundamentals' },
    { id: '3', name: 'Chemistry Lab' },
    { id: '4', name: 'Biology Basics' },
  ]);
  const handleAddClass = () => {
    const newClass: ClassData = {
      id: uuidv4(),
      name: `New Class ${classes.length + 1}`,
    };
    setClasses(prev => [...prev, newClass]);
  };
  const router = useRouter();
  const handleViewClass = (id: string) => {

        router.push(`/teacher/${id}`);
  };

  const handleEditClass = (id: string, newName: string) => {
    setClasses(prev => 
      prev.map(cls => 
        cls.id === id ? { ...cls, name: newName } : cls
      )
    );
  };

  const handleDeleteClass = (id: string) => {
    setClasses(prev => prev.filter(cls => cls.id !== id));
  };

  return (
    <div className={styles.dashboard}>
      <Navigation 
        userRole="teacher" 
        userName="Dr. Sarah Johnson" 
      />
      
      <main className={styles.container}>
      

        <div className={styles.classesSection}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Classes</h2>
            <div className={styles.classCount}>
              {classes.length} {classes.length === 1 ? 'class' : 'classes'}
            </div>
          </div>

          {classes.length === 0 ? (
            <div className={styles.emptyState}>
              <svg className={styles.emptyStateIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <h3 className={styles.emptyStateTitle}>No classes yet</h3>
              <p className={styles.emptyStateText}>Create your first class to get started</p>
            </div>
          ) : (
            <div className={styles.classesGrid}>
                <AddClassCard onAddClass={handleAddClass} />
                        {classes.slice().reverse().map((classItem) => (
                <ClassCard
                    key={classItem.id}
                    id={classItem.id}
                    name={classItem.name}
                    onView={handleViewClass}
                    onEdit={handleEditClass}
                    onDelete={handleDeleteClass}
                />
                ))}
            </div>
          )}

          {classes.length === 0 && (
            <div style={{ marginTop: 'var(--spacing-6)' }}>
              <AddClassCard onAddClass={handleAddClass} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}