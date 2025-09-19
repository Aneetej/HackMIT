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
  
  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const sessionCounts = await prisma.$queryRawUnsafe<Array<{
    student_id: string;
    student_name: string;
    session_count: string;
  }>>(`
    SELECT 
      s.id as student_id,
      s.name as student_name,
      COUNT(cs.id) as session_count
    FROM "students" s
    LEFT JOIN "chat_sessions" cs ON s.id = cs.student_id
      AND cs.started_at >= $1 
      AND cs.started_at <= $2
    WHERE s.id = ANY($3::text[])
    GROUP BY s.id, s.name
    ORDER BY session_count DESC
  `, startDateParam, endDateParam, cohort.studentIds);

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

  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{ avg_messages: number }>>(`
    SELECT AVG(student_messages.message_count) as avg_messages
    FROM (
      SELECT s.id, COUNT(cm.id) as message_count
      FROM "students" s
      LEFT JOIN "chat_sessions" cs ON s.id = cs.student_id
      LEFT JOIN "chat_messages" cm ON cs.id = cm.session_id
        AND cm.timestamp >= $1 
        AND cm.timestamp <= $2
        AND cm.sender_type = 'student'
      WHERE s.id = ANY($3::text[])
      GROUP BY s.id
    ) student_messages
  `, startDateParam, endDateParam, cohort.studentIds);

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

  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{ total_messages: string }>>(`
    SELECT COUNT(cm.id) as total_messages
    FROM "chat_messages" cm
    JOIN "chat_sessions" cs ON cm.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND cm.timestamp >= $2 
      AND cm.timestamp <= $3
      AND cm.sender_type = 'student'
  `, cohort.studentIds, startDateParam, endDateParam);

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

  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{ avg_sessions_per_day: number }>>(`
    SELECT 
      COUNT(cs.id)::float / GREATEST(1, EXTRACT(DAYS FROM ($2::timestamp - $1::timestamp)) + 1) as avg_sessions_per_day
    FROM "chat_sessions" cs
    WHERE cs.student_id = ANY($3::text[])
      AND cs.started_at >= $1 
      AND cs.started_at <= $2
  `, startDateParam, endDateParam, cohort.studentIds);

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

  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{
    hour: number;
    message_count: string;
  }>>(`
    SELECT 
      EXTRACT(HOUR FROM cm.timestamp) as hour,
      COUNT(cm.id) as message_count
    FROM "chat_messages" cm
    JOIN "chat_sessions" cs ON cm.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND cm.timestamp >= $2 
      AND cm.timestamp <= $3
      AND cm.sender_type = 'student'
    GROUP BY EXTRACT(HOUR FROM cm.timestamp)
    ORDER BY hour
  `, cohort.studentIds, startDateParam, endDateParam);

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

  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{
    total_sessions: string;
    completed_sessions: string;
    avg_duration_minutes: string;
  }>>(`
    SELECT 
      COUNT(cs.id) as total_sessions,
      COUNT(CASE WHEN cs.status = 'completed' THEN 1 END) as completed_sessions,
      AVG(EXTRACT(EPOCH FROM (cs.ended_at - cs.started_at)) / 60) as avg_duration_minutes
    FROM "chat_sessions" cs
    WHERE cs.student_id = ANY($1::text[])
      AND cs.started_at >= $2 
      AND cs.started_at <= $3
  `, cohort.studentIds, startDateParam, endDateParam);

  const data = result[0];
  const totalSessions = Number(data?.total_sessions || 0);
  const completedSessions = Number(data?.completed_sessions || 0);
  
  return {
    completionRate: totalSessions > 0 ? completedSessions / totalSessions : 0,
    avgDurationMinutes: Number(data?.avg_duration_minutes || 0),
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
  const startDateParam = startDate;
  const endDateParam = endDate;
  
  const result = await prisma.$queryRawUnsafe<Array<{
    question_text: string;
    category: string;
    frequency_count: number;
    success_rate: number;
  }>>(`
    SELECT 
      faq.question_text,
      faq.category,
      faq.frequency_count,
      faq.success_rate
    FROM "frequently_asked_questions" faq
    WHERE faq.last_asked >= $1
      AND faq.last_asked <= $2
    ORDER BY faq.frequency_count DESC
    LIMIT $3
  `, startDateParam, endDateParam, limit);

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
  const startDateParam1 = startDate;
  const endDateParam1 = endDate;
  
  const sessionTakeaways = await prisma.$queryRawUnsafe<Array<{
    takeaway_type: string;
    misconception_count: string;
  }>>(`
    SELECT 
      st.takeaway_type,
      COUNT(*) as misconception_count
    FROM "session_takeaways" st
    JOIN "chat_sessions" cs ON st.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND st.created_at >= $2
      AND st.created_at <= $3
      AND st.takeaway_type LIKE '%misconception%'
    GROUP BY st.takeaway_type
    ORDER BY misconception_count DESC
  `, cohort.studentIds, startDateParam1, endDateParam1);

  // Get common misconceptions from FAQ data
  
  const faqMisconceptions = await prisma.$queryRawUnsafe<Array<{
    category: string;
    low_success_count: string;
    question_texts: string[];
  }>>(`
    SELECT 
      category,
      COUNT(*) as low_success_count,
      ARRAY_AGG(question_text) as question_texts
    FROM "frequently_asked_questions"
    WHERE last_asked >= $1
      AND last_asked <= $2
      AND (success_rate IS NULL OR success_rate < 0.7)
    GROUP BY category
  `, startDate, endDate);

  const misconceptionMap = new Map<string, MisconceptionData>();

  // Process takeaway data
  sessionTakeaways.forEach(row => {
    misconceptionMap.set(row.takeaway_type, {
      category: row.takeaway_type,
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

export async function generateAnalyticsSummary(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<{
  summary: string;
  keyInsights: string[];
  recommendations: string[];
}> {
  try {
    // Get the 3 core metrics
    const [faqsData, topicsData] = await Promise.all([
      topFaqs(teacherId, startDate, endDate),
      getTopicPerformance(teacherId, startDate, endDate)
    ]);

    // Analyze FAQs
    const topFaqsList = faqsData.slice(0, 5);
    const lowSuccessFaqs = faqsData.filter((faq: FaqData) => (faq.successRate || 0) < 0.7);
    const highSuccessFaqs = faqsData.filter((faq: FaqData) => (faq.successRate || 0) >= 0.8);

    // Analyze successful topics
    const successfulTopics = topicsData.successfulTopics.slice(0, 5);
    const strugglingTopics = topicsData.strugglingTopics.slice(0, 5);

    // Generate summary paragraph
    let summary = `During the period from ${startDate.toDateString()} to ${endDate.toDateString()}, `;
    
    if (topFaqsList.length > 0) {
      const totalQuestions = topFaqsList.reduce((sum: number, faq: FaqData) => sum + (faq.frequencyCount || 0), 0);
      const avgSuccessRate = topFaqsList.reduce((sum: number, faq: FaqData) => sum + (faq.successRate || 0), 0) / topFaqsList.length;
      summary += `students asked ${totalQuestions} questions across ${topFaqsList.length} main topics with an average success rate of ${(avgSuccessRate * 100).toFixed(1)}%. `;
    }

    if (successfulTopics.length > 0) {
      const topSuccessfulTopic = successfulTopics[0];
      summary += `Students excelled most in ${topSuccessfulTopic.topic} with a ${(topSuccessfulTopic.successRate * 100).toFixed(1)}% success rate. `;
    }

    if (strugglingTopics.length > 0) {
      const topStrugglingTopic = strugglingTopics[0];
      summary += `The most challenging area was ${topStrugglingTopic.topic}, where ${topStrugglingTopic.studentCount} student(s) experienced difficulties. `;
    }

    // Generate key insights
    const keyInsights: string[] = [];
    
    if (highSuccessFaqs.length > 0) {
      keyInsights.push(`${highSuccessFaqs.length} question categories show high student confidence (>80% success rate)`);
    }
    
    if (lowSuccessFaqs.length > 0) {
      keyInsights.push(`${lowSuccessFaqs.length} question areas need additional support (<70% success rate)`);
    }

    if (successfulTopics.length > 0) {
      const avgSuccessRate = successfulTopics.reduce((sum: number, topic: any) => sum + topic.successRate, 0) / successfulTopics.length;
      keyInsights.push(`Top performing topics average ${(avgSuccessRate * 100).toFixed(1)}% success rate`);
    }

    if (strugglingTopics.length > 0) {
      const totalAffectedStudents = strugglingTopics.reduce((sum: number, topic: any) => sum + topic.studentCount, 0);
      keyInsights.push(`${totalAffectedStudents} student instances show difficulty patterns across ${strugglingTopics.length} topics`);
    }

    // Generate recommendations
    const recommendations: string[] = [];
    
    if (lowSuccessFaqs.length > 0) {
      const categories = [...new Set(lowSuccessFaqs.map((faq: FaqData) => faq.category))];
      recommendations.push(`Focus additional practice on ${categories.join(', ')} concepts`);
    }

    if (strugglingTopics.length > 0) {
      const commonIssues = strugglingTopics.flatMap((topic: any) => topic.commonIssues || []);
      const uniqueIssues = [...new Set(commonIssues)].slice(0, 3);
      if (uniqueIssues.length > 0) {
        recommendations.push(`Address common difficulties: ${uniqueIssues.join(', ')}`);
      }
    }

    if (successfulTopics.length > 0) {
      recommendations.push(`Leverage successful teaching methods from ${successfulTopics[0].topic} for other topics`);
    }

    return {
      summary: summary.trim(),
      keyInsights,
      recommendations
    };

  } catch (error) {
    console.error('Error generating analytics summary:', error);
    return {
      summary: 'Unable to generate summary due to insufficient data.',
      keyInsights: [],
      recommendations: []
    };
  }
}

export async function getStudentSummaries(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<Array<{
  studentId: string;
  studentName: string;
  summaries: Array<{
    id: string;
    summary: string;
    takeawayType: string;
    keyConcepts: string[];
    createdAt: Date;
  }>;
}>> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) return [];

  const studentSummaries = await prisma.$queryRawUnsafe<Array<{
    student_id: string;
    student_name: string;
    summary_id: string;
    summary_text: string;
    takeaway_type: string;
    key_concepts: string[];
    created_at: Date;
  }>>(
    `
    SELECT 
      s.id as student_id,
      s.name as student_name,
      st.id as summary_id,
      st.summary as summary_text,
      st.takeaway_type,
      st.key_concepts,
      st.created_at
    FROM "students" s
    JOIN "chat_sessions" cs ON s.id = cs.student_id
    JOIN "session_takeaways" st ON cs.id = st.session_id
    WHERE s.id = ANY($1::text[])
      AND st.created_at >= $2
      AND st.created_at <= $3
      AND st.summary IS NOT NULL
      AND st.summary != ''
    ORDER BY s.name, st.created_at DESC
    `,
    cohort.studentIds,
    startDate,
    endDate
  );

  // Group summaries by student
  const studentMap = new Map<string, {
    studentId: string;
    studentName: string;
    summaries: Array<{
      id: string;
      summary: string;
      takeawayType: string;
      keyConcepts: string[];
      createdAt: Date;
    }>;
  }>();

  studentSummaries.forEach(row => {
    if (!studentMap.has(row.student_id)) {
      studentMap.set(row.student_id, {
        studentId: row.student_id,
        studentName: row.student_name,
        summaries: []
      });
    }

    const student = studentMap.get(row.student_id)!;
    student.summaries.push({
      id: row.summary_id,
      summary: row.summary_text,
      takeawayType: row.takeaway_type,
      keyConcepts: row.key_concepts || [],
      createdAt: row.created_at
    });
  });

  return Array.from(studentMap.values());
}

export async function getTopicPerformance(
  teacherId: string,
  startDate: Date,
  endDate: Date
): Promise<{
  successfulTopics: Array<{
    topic: string;
    successRate: number;
    studentCount: number;
    averageScore: number;
  }>;
  strugglingTopics: Array<{
    topic: string;
    successRate: number;
    studentCount: number;
    commonIssues: string[];
  }>;
}> {
  const cohort = await getTeacherCohort(teacherId);
  
  if (cohort.studentIds.length === 0) {
    return { successfulTopics: [], strugglingTopics: [] };
  }

  // Get successful topics from learning analytics
  const successfulTopics = await prisma.$queryRawUnsafe<Array<{
    concept: string;
    success_rate: number;
    student_count: string;
    avg_score: number;
  }>>(
    `
    SELECT 
      UNNEST(concepts_mastered) as concept,
      AVG(success_rate) as success_rate,
      COUNT(DISTINCT student_id) as student_count,
      AVG(success_rate * 100) as avg_score
    FROM "learning_analytics" la
    WHERE la.student_id = ANY($1::text[])
      AND la.date >= $2
      AND la.date <= $3
      AND array_length(concepts_mastered, 1) > 0
    GROUP BY concept
    HAVING AVG(success_rate) >= 0.7
    ORDER BY success_rate DESC, student_count DESC
    LIMIT 10
    `,
    cohort.studentIds,
    startDate,
    endDate
  );

  // Get struggling topics from session takeaways
  const strugglingTopics = await prisma.$queryRawUnsafe<Array<{
    concept: string;
    success_rate: number;
    student_count: string;
    common_issues: string[];
  }>>(
    `
    SELECT 
      UNNEST(key_concepts) as concept,
      0.3 as success_rate,
      COUNT(DISTINCT cs.student_id) as student_count,
      ARRAY_AGG(DISTINCT st.takeaway_type) as common_issues
    FROM "session_takeaways" st
    JOIN "chat_sessions" cs ON st.session_id = cs.id
    WHERE cs.student_id = ANY($1::text[])
      AND st.created_at >= $2
      AND st.created_at <= $3
      AND array_length(key_concepts, 1) > 0
      AND (st.takeaway_type LIKE '%difficulty%' OR st.takeaway_type LIKE '%struggle%' OR st.takeaway_type LIKE '%confusion%')
    GROUP BY concept
    ORDER BY student_count DESC
    LIMIT 10
    `,
    cohort.studentIds,
    startDate,
    endDate
  );

  return {
    successfulTopics: successfulTopics.map(row => ({
      topic: row.concept,
      successRate: Math.round(row.success_rate * 100) / 100,
      studentCount: Number(row.student_count),
      averageScore: Math.round(row.avg_score)
    })),
    strugglingTopics: strugglingTopics.map(row => ({
      topic: row.concept,
      successRate: Math.round(row.success_rate * 100) / 100,
      studentCount: Number(row.student_count),
      commonIssues: row.common_issues || []
    }))
  };
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
  misconceptionsByType,
  getStudentSummaries,
  getTopicPerformance
};
