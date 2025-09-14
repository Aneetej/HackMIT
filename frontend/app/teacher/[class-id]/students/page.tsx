'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import StudentCard from '../../../../components/StudentCard';
import { teacherApi, StudentData } from '../../../../lib/teacher/apis';
import styles from './page.module.css';

export default function StudentsPage({ params }: { params: Promise<{ 'class-id': string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const classId = resolvedParams['class-id'];

  const [students, setStudents] = useState<StudentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        setLoading(true);
        const response = await teacherApi.getClassStudents(classId);
        if (response.success) {
          setStudents(response.students);
        } else {
          setError('Failed to load students');
        }
      } catch (err) {
        console.error('Error fetching students:', err);
        setError('Failed to load students');
      } finally {
        setLoading(false);
      }
    };

    fetchStudents();
  }, [classId]);

  const handleViewStudent = (studentId: string) => {
    router.push(`/teacher/${classId}/students/${studentId}`);
  };

  if (loading) {
    return (
      <div className={styles.studentsGrid}>
        <div>Loading students...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.studentsGrid}>
        <div>Error: {error}</div>
      </div>
    );
  }

  if (students.length === 0) {
    return (
      <div className={styles.studentsGrid}>
        <div>No students have joined this class yet.</div>
      </div>
    );
  }

  return (
    <div className={styles.studentsGrid}>
      {students.map((student) => (
        <StudentCard
          key={student.id}
          id={student.id}
          name={student.name}
          onView={handleViewStudent}
        />
      ))}
    </div>
  );
}
