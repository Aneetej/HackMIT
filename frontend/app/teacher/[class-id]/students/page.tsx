'use client';

import { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import StudentCard from '../../../../components/StudentCard';
import styles from './page.module.css';

interface Student {
  id: string;
  name: string;
}

export default function StudentsPage({ params }: { params: Promise<{ 'class-id': string }> }) {
  const router = useRouter();
  const resolvedParams = use(params);
  const classId = resolvedParams['class-id'];

  const [students, setStudents] = useState<Student[]>([
    { id: '1', name: 'Student Name' },
    { id: '2', name: 'Student Name' },
    { id: '3', name: 'Student Name' },
  ]);

  const handleViewStudent = (studentId: string) => {
    router.push(`/teacher/${classId}/students/${studentId}`);
  };

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
