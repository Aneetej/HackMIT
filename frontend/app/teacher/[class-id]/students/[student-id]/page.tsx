'use client';

import { use, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { ChartContainer } from '../../../../../components/ui/chart';
import { teacherApi, StudentDailyUsageData, NoteData } from '../../../../../lib/teacher/apis';
import CommonStruggle from '../../../../../components/CommonStruggle';
import styles from './page.module.css';

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
  const [noteId, setNoteId] = useState<string | null>(null);
  const [noteLoading, setNoteLoading] = useState(true);
  const [areasOfStruggle, setAreasOfStruggle] = useState('Student shows difficulty with algebra equations, word problems, and fractions. Also struggles with time management during tests and experiences test anxiety.');
  const [usageData, setUsageData] = useState<StudentDailyUsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setNoteLoading(true);
        
        // Fetch student usage data and note in parallel
        const [usageResponse, noteResponse] = await Promise.all([
          teacherApi.getStudentDailyUsage(classId, studentId),
          teacherApi.getNote(classId, studentId)
        ]);
        
        if (usageResponse.success) {
          setUsageData(usageResponse.data);
        } else {
          setError('Failed to load student usage data');
        }
        
        if (noteResponse.success) {
          setNotes(noteResponse.note.content);
          setNoteId(noteResponse.note.id);
        } else {
          console.error('Failed to load note:', noteResponse);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load student data');
      } finally {
        setLoading(false);
        setNoteLoading(false);
      }
    };

    fetchData();
  }, [classId, studentId]);

  // Transform usage data for chart
  const chartData = usageData ? usageData.dailyUsage.map(day => ({
    day: day.day,
    usage: day.messageCount
  })) : [];

  const handleBack = () => {
    router.push(`/teacher/${classId}/students`);
  };

  const handleAreaChange = (value: string) => {
    setAreasOfStruggle(value);
  };

  const handleNotesChange = async (value: string) => {
    setNotes(value);
    
    // Debounce the API call to avoid too many requests
    try {
      const response = await teacherApi.updateNote(classId, studentId, { content: value });
      if (response.success) {
        setNoteId(response.note.id);
      } else {
        console.error('Failed to update note:', response);
      }
    } catch (err) {
      console.error('Error updating note:', err);
    }
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
        <h1 className={styles.studentName}>{usageData?.studentName || 'Loading...'}</h1>
      </div>
      
      <div className={styles.dashboardGrid}>
        <div className={styles.notesSection}>
          <h2 className={styles.sectionTitle}>Notes:</h2>
          {noteLoading ? (
            <div className={styles.loadingState}>Loading note...</div>
          ) : (
            <textarea
              className={styles.notesTextarea}
              value={notes}
              onChange={(e) => handleNotesChange(e.target.value)}
              placeholder="Add notes about this student..."
            />
          )}
        </div>

        <CommonStruggle 
          struggles={areasOfStruggle}
          title="Areas of struggle"
          editable={true}
          onStruggleChange={handleAreaChange}
        />

        <div className={styles.chartSection}>
          <h2 className={styles.sectionTitle}>Daily message activity</h2>
          {loading ? (
            <div className={styles.loadingState}>Loading usage data...</div>
          ) : error ? (
            <div className={styles.errorState}>Error: {error}</div>
          ) : usageData ? (
            <>
              <div className={styles.usageStats}>
                <div className={styles.statItem}>
                  <span className={styles.statLabel}>Total Messages:</span>
                  <span className={styles.statValue}>{usageData.totalMessages}</span>
                </div>
                <div className={styles.statItem}>
                  <span className={styles.statLabel}>Daily Average:</span>
                  <span className={styles.statValue}>{usageData.averageDailyMessages.toFixed(1)}</span>
                </div>
              </div>
              <div className={styles.chartContainer}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
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
                      formatter={(value) => [`${value} messages`, 'Messages']}
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
            </>
          ) : (
            <div className={styles.emptyState}>No usage data available</div>
          )}
        </div>
      </div>
    </>
  );
}
