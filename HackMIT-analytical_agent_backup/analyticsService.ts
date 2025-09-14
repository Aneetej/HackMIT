import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export interface TeacherCohort {
  teacherId: string;
  studentIds: string[];
  studentCount: number;
}

export interface SessionsPerStudent {
  studentId: string;
  studentName: string;
  sessionCount: number;
}

export interface HourlyMessageData {
  hour: number;
  messageCount: number;
}

export interface CompletionData {
  completionRate: number;
  avgDurationMinutes: number;
  totalSessions: number;
  completedSessions: number;
}

export interface FaqData {
  questionText: string;
  category: string;
  frequencyCount: number;
  successRate: number | null;
}

export interface MisconceptionData {
  category: string;
  commonMisconceptions: string[];
  frequency: number;
}

/**
 * Get the cohort of students supervised by a teacher
 */
export async function getTeacherCohort(teacherId: string): Promise<TeacherCohort> {
  const teacher = await prisma.teacher.findUnique({
    where: { id: teacherId },
    select: { supervised_students: true }
  });

  if (!teacher) {
    throw new Error(`Teacher with ID ${teacherId} not found`);
  }

  return {
    teacherId,
    studentIds: teacher.supervised_students,
    studentCount: teacher.supervised_students.length
  };
}

/**
 * Get session count per student for a teacher's cohort within date range
 */
export async function sessionsPerStudent(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<SessionsPerStudent[]> {
  const cohort = await getTeacherCohort(teacherId);
  
  const sessionCounts = await prisma.$queryRawUnsafe<Array<{student_id: string, student_name: string, session_count: bigint}>>`
    SELECT 
      s.id as student_id,
      s.name as student_name,
      COUNT(cs.id) as session_count
    FROM students s
    LEFT JOIN chat_sessions cs ON s.id = cs.student_id 
      AND cs.started_at >= $1 
      AND cs.started_at <= $2
    WHERE s.id = ANY($3::text[])
    GROUP BY s.id, s.name
    ORDER BY session_count DESC
  `, startDate, endDate, cohort.studentIds);

  return sessionCounts.map(row => ({
    studentId: row.student_id,
    studentName: row.student_name,
    sessionCount: Number(row.session_count)
  }));
}

/**
 * Get average messages per student for a teacher's cohort within date range
 */
export async function avgMessagesPerStudent(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<number> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return 0;

  const result = await prisma.$queryRawUnsafe<Array<{avg_messages: number}>>`
    SELECT 
      AVG(message_count) as avg_messages
    FROM (
      SELECT 
        s.id,
        COUNT(cm.id) as message_count
      FROM students s
      LEFT JOIN chat_sessions cs ON s.id = cs.student_id
      LEFT JOIN chat_messages cm ON cs.id = cm.session_id
        AND cm.timestamp >= $1 
        AND cm.timestamp <= $2
        AND cm.sender_type = 'student'
      WHERE s.id = ANY($3::text[])
      GROUP BY s.id
    ) student_messages
  `, startDate, endDate, cohort.studentIds);

  return result[0]?.avg_messages || 0;
}

/**
 * Get average messages per class (total messages / total students) within date range
 */
export async function avgMessagesPerClass(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<number> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return 0;

  const result = await prisma.$queryRawUnsafe<Array<{total_messages: bigint}>>`
    SELECT COUNT(cm.id) as total_messages
    FROM chat_messages cm
    JOIN chat_sessions cs ON cm.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND cm.timestamp >= $2 
      AND cm.timestamp <= $3
      AND cm.sender_type = 'student'
  `, cohort.studentIds, startDate, endDate);

  const totalMessages = Number(result[0]?.total_messages || 0);
  return totalMessages / cohort.studentCount;
}

/**
 * Get average sessions per day for a teacher's cohort within date range
 */
export async function avgSessionsPerDay(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<number> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return 0;

  const result = await prisma.$queryRawUnsafe<Array<{avg_sessions_per_day: number}>>`
    SELECT 
      COUNT(cs.id)::float / GREATEST(DATE_PART('day', $2::timestamp - $1::timestamp), 1) as avg_sessions_per_day
    FROM chat_sessions cs
    WHERE cs.student_id = ANY($3::text[])
      AND cs.started_at >= $1 
      AND cs.started_at <= $2
  `, startDate, endDate, cohort.studentIds);

  return result[0]?.avg_sessions_per_day || 0;
}

/**
 * Get hourly message histogram for a teacher's cohort within date range
 */
export async function hourlyMessageHistogram(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<HourlyMessageData[]> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return [];

  const result = await prisma.$queryRawUnsafe<Array<{hour: number, message_count: bigint}>>`
    SELECT 
      EXTRACT(HOUR FROM cm.timestamp) as hour,
      COUNT(cm.id) as message_count
    FROM chat_messages cm
    JOIN chat_sessions cs ON cm.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND cm.timestamp >= $2 
      AND cm.timestamp <= $3
      AND cm.sender_type = 'student'
    GROUP BY EXTRACT(HOUR FROM cm.timestamp)
    ORDER BY hour
  `, cohort.studentIds, startDate, endDate);

  return result.map(row => ({
    hour: row.hour,
    messageCount: Number(row.message_count)
  }));
}

/**
 * Get completion rate and average duration for a teacher's cohort within date range
 */
export async function completionRateAndAvgDuration(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<CompletionData> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) {
    return {
      completionRate: 0,
      avgDurationMinutes: 0,
      totalSessions: 0,
      completedSessions: 0
    };
  }

  const result = await prisma.$queryRawUnsafe<Array<{
    total_sessions: bigint,
    completed_sessions: bigint,
    avg_duration_minutes: number
  }>>`
    SELECT 
      COUNT(*) as total_sessions,
      COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
      AVG(
        CASE 
          WHEN ended_at IS NOT NULL 
          THEN EXTRACT(EPOCH FROM (ended_at - started_at)) / 60.0 
          ELSE NULL 
        END
      ) as avg_duration_minutes
    FROM chat_sessions cs
    WHERE cs.student_id = ANY($1::text[])
      AND cs.started_at >= $2 
      AND cs.started_at <= $3
  `, cohort.studentIds, startDate, endDate);

  const data = result[0];
  const totalSessions = Number(data?.total_sessions || 0);
  const completedSessions = Number(data?.completed_sessions || 0);
  
  return {
    completionRate: totalSessions > 0 ? completedSessions / totalSessions : 0,
    avgDurationMinutes: data?.avg_duration_minutes || 0,
    totalSessions,
    completedSessions
  };
}

/**
 * Get top FAQs for a teacher's cohort within date range
 */
export async function topFaqs(
  teacherId: string,
  startDate: Date,
  endDate: Date,
  limit: number = 10
): Promise<FaqData[]> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return [];

  // Get FAQs that were asked by students in the cohort during the date range
  const result = await prisma.$queryRawUnsafe<Array<{
    question_text: string,
    category: string,
    frequency_count: number,
    success_rate: number | null
  }>>`
    SELECT DISTINCT
      faq.question_text,
      faq.category,
      faq.frequency_count,
      faq.success_rate
    FROM frequently_asked_questions faq
    WHERE faq.last_asked >= $1 
      AND faq.last_asked <= $2
    ORDER BY faq.frequency_count DESC
    LIMIT $3
  `, startDate, endDate, limit);

  return result.map(row => ({
    questionText: row.question_text,
    category: row.category,
    frequencyCount: row.frequency_count,
    successRate: row.success_rate
  }));
}

/**
 * Get misconceptions by type for a teacher's cohort within date range
 */
export async function misconceptionsByType(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<MisconceptionData[]> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return [];

  // Analyze session takeaways for misconception patterns
  const result = await prisma.$queryRawUnsafe<Array<{
    category: string,
    misconception_count: bigint
  }>>`
    SELECT 
      unnest(st.key_concepts) as category,
      COUNT(*) as misconception_count
    FROM session_takeaways st
    JOIN chat_sessions cs ON st.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND st.created_at >= $2 
      AND st.created_at <= $3
      AND st.takeaway_type LIKE '%misconception%'
    GROUP BY category
    ORDER BY misconception_count DESC
  `, cohort.studentIds, startDate, endDate);

  // Get common misconceptions from FAQ data
  const faqMisconceptions = await prisma.$queryRawUnsafe<Array<{
    category: string,
    question_texts: string[]
  }>>`
    SELECT 
      category,
      array_agg(question_text) as question_texts
    FROM frequently_asked_questions
    WHERE category IS NOT NULL
      AND last_asked >= $1 
      AND last_asked <= $2
      AND (success_rate IS NULL OR success_rate < 0.7)
    GROUP BY category
  `, startDate, endDate);

  const misconceptionMap = new Map<string, MisconceptionData>();

  // Process takeaway data
  result.forEach(row => {
    misconceptionMap.set(row.category, {
      category: row.category,
      commonMisconceptions: [],
      frequency: Number(row.misconception_count)
    });
  });

  // Add FAQ misconceptions
  faqMisconceptions.forEach(row => {
    const existing = misconceptionMap.get(row.category);
    if (existing) {
      existing.commonMisconceptions = row.question_texts;
    } else {
      misconceptionMap.set(row.category, {
        category: row.category,
        commonMisconceptions: row.question_texts,
        frequency: row.question_texts.length
      });
    }
  });

  return Array.from(misconceptionMap.values())
    .sort((a, b) => b.frequency - a.frequency);
}

export default {
  getTeacherCohort,
  sessionsPerStudent,
  avgMessagesPerStudent,
  avgMessagesPerClass,
  avgSessionsPerDay,
  hourlyMessageHistogram,
  completionRateAndAvgDuration,
  topFaqs,
  misconceptionsByType
};
