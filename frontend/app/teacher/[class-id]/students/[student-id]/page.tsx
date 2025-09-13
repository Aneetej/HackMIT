'use client';

import { use, useState } from 'react';
import { useRouter } from 'next/navigation';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { ChartContainer } from '../../../../../components/ui/chart';
import styles from './page.module.css';

const usageData = [
  { day: 'Mon', usage: 65 },
  { day: 'Tue', usage: 45 },
  { day: 'Wed', usage: 55 },
  { day: 'Thu', usage: 80 },
  { day: 'Fri', usage: 70 },
  { day: 'Sat', usage: 35 },
  { day: 'Sun', usage: 60 },
];

export default function StudentDetailPage({ 
  params 
}: { 
  params: Promise<{ 'class-id': string; 'student-id': string }> 
}) {
  const router = useRouter();
  const resolvedParams = use(params);
  const classId = resolvedParams['class-id'];
  const studentId = resolvedParams['student-id'];

  const [notes, setNotes] = useState('');
  const [areasOfStruggle, setAreasOfStruggle] = useState(['Algebra equations', 'Word problems', 'Fractions', 'Time management', 'Test anxiety']);

  const handleBack = () => {
    router.push(`/teacher/${classId}/students`);
  };

  const handleAreaChange = (index: number, value: string) => {
    const newAreas = [...areasOfStruggle];
    newAreas[index] = value;
    setAreasOfStruggle(newAreas);
  };

  return (
    <>
      <div className={styles.studentHeader}>
        <button className={styles.backToStudentsButton} onClick={handleBack}>
          <svg className={styles.backIcon} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to All Students
        </button>
        <h1 className={styles.studentName}>Alex Johnson</h1>
      </div>
      
      <div className={styles.dashboardGrid}>
        <div className={styles.notesSection}>
          <h2 className={styles.sectionTitle}>Notes:</h2>
          <textarea
            className={styles.notesTextarea}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder=""
          />
        </div>

        <div className={styles.areasSection}>
          <h2 className={styles.sectionTitle}>Areas of struggle</h2>
          <div className={styles.areasInputs}>
            {areasOfStruggle.map((area, index) => (
              <input
                key={index}
                type="text"
                className={styles.areaInput}
                value={area}
                onChange={(e) => handleAreaChange(index, e.target.value)}
placeholder=""
              />
            ))}
          </div>
        </div>

        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>Average usage by day</h2>
          <div className={styles.chartContainer}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={usageData}>
                <XAxis 
                  dataKey="day" 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                />
                <YAxis 
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                  width={30}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: 'var(--radius)',
                    color: 'hsl(var(--foreground))',
                    fontSize: '12px'
                  }}
                  labelStyle={{ color: 'hsl(var(--foreground))' }}
                  formatter={(value) => [`${value} minutes`, 'Usage']}
                  labelFormatter={(label) => `${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="usage" 
                  stroke="hsl(var(--primary))" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </>
  );
}
