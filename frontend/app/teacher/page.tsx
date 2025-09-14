'use client';

import { useState, useEffect } from 'react';
import ClassCard from '../../components/ClassCard';
import AddClassCard from '../../components/AddClassCard';
import styles from './page.module.css';
import { useRouter } from 'next/navigation';
import { teacherApi, ClassData } from '../../lib/teacher/apis';

interface UserData {
  userType: 'student' | 'teacher';
  userId: string;
}

export default function TeacherDashboard() {
  const [classes, setClasses] = useState<ClassData[]>([]);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Get user data from localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUserData(parsedUser);
        if (parsedUser.userType === 'teacher') {
          loadClasses(parsedUser.userId);
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
      }
    }
    setIsLoading(false);
  }, []);

  const loadClasses = async (teacherId: string) => {
    try {
      const response = await teacherApi.getClasses(teacherId);
      setClasses(response.classes);
    } catch (error) {
      console.error('Error loading classes:', error);
    }
  };

  const handleCreateClass = async (className: string) => {
    if (!userData) return;
    
    try {
      const response = await teacherApi.createClass(userData.userId, { name: className });
      if (response.success) {
        setClasses(prev => [response.class, ...prev]);
      }
    } catch (error) {
      console.error('Error creating class:', error);
    }
  };
  const router = useRouter();
  const handleViewClass = (id: string) => {

        router.push(`/teacher/${id}`);
  };

  const handleEditClass = async (id: string, newName: string) => {
    try {
      const response = await teacherApi.updateClass(id, { name: newName });
      if (response.success) {
        setClasses(prev => 
          prev.map(cls => 
            cls.id === id ? { ...cls, name: newName } : cls
          )
        );
      }
    } catch (error) {
      console.error('Error updating class:', error);
    }
  };

  const handleDeleteClass = async (id: string) => {
    try {
      const response = await teacherApi.deleteClass(id);
      if (response.success) {
        setClasses(prev => prev.filter(cls => cls.id !== id));
      }
    } catch (error) {
      console.error('Error deleting class:', error);
    }
  };

  return (
    <div className={styles.dashboard}>
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
                <AddClassCard onCreateClass={handleCreateClass} />
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
              <AddClassCard onCreateClass={handleCreateClass} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}