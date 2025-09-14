import express from 'express';
import {
  getTeacherCohort,
  sessionsPerStudent,
  avgMessagesPerStudent,
  avgMessagesPerClass,
  avgSessionsPerDay,
  hourlyMessageHistogram,
  completionRateAndAvgDuration,
  topFaqs,
  misconceptionsByType
} from './analyticsService';

const router = express.Router();

/**
 * Validate and parse date parameters
 */
function validateDateParams(startStr?: string, endStr?: string): { start: Date; end: Date } {
  if (!startStr || !endStr) {
    throw new Error('Both start and end date parameters are required');
  }

  const start = new Date(startStr);
  const end = new Date(endStr);

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    throw new Error('Invalid date format. Use ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss)');
  }

  if (start >= end) {
    throw new Error('Start date must be before end date');
  }

  return { start, end };
}

/**
 * GET /teacher/:teacherId/overview
 * Returns comprehensive overview metrics for a teacher's cohort
 */
router.get('/teacher/:teacherId/overview', async (req, res) => {
  try {
    const { teacherId } = req.params;
    const { start, end } = validateDateParams(req.query.start as string, req.query.end as string);

    // Fetch all overview metrics in parallel
    const [
      cohort,
      sessionsData,
      avgMessagesStudent,
      avgMessagesClass,
      avgSessionsDaily,
      completionData,
      topMisconceptions
    ] = await Promise.all([
      getTeacherCohort(teacherId),
      sessionsPerStudent(teacherId, start, end),
      avgMessagesPerStudent(teacherId, start, end),
      avgMessagesPerClass(teacherId, start, end),
      avgSessionsPerDay(teacherId, start, end),
      completionRateAndAvgDuration(teacherId, start, end),
      misconceptionsByType(teacherId, start, end)
    ]);

    const response = {
      teacherId,
      dateRange: {
        start: start.toISOString(),
        end: end.toISOString()
      },
      cohortInfo: {
        totalStudents: cohort.studentCount,
        studentIds: cohort.studentIds
      },
      engagementMetrics: {
        avgMessagesPerStudent: Math.round(avgMessagesStudent * 100) / 100,
        avgMessagesPerClass: Math.round(avgMessagesClass * 100) / 100,
        avgSessionsPerDay: Math.round(avgSessionsDaily * 100) / 100
      },
      sessionMetrics: {
        totalSessions: completionData.totalSessions,
        completedSessions: completionData.completedSessions,
        completionRate: Math.round(completionData.completionRate * 10000) / 100, // percentage
        avgDurationMinutes: Math.round(completionData.avgDurationMinutes * 100) / 100
      },
      studentActivity: sessionsData.map(student => ({
        studentId: student.studentId,
        studentName: student.studentName,
        sessionCount: student.sessionCount
      })),
      topMisconceptions: topMisconceptions.slice(0, 5).map(misconception => ({
        category: misconception.category,
        frequency: misconception.frequency,
        commonIssues: misconception.commonMisconceptions.slice(0, 3)
      }))
    };

    res.json(response);
  } catch (error) {
    console.error('Error in /teacher/:teacherId/overview:', error);
    res.status(400).json({
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

/**
 * GET /teacher/:teacherId/hourly
 * Returns hourly message distribution for a teacher's cohort
 */
router.get('/teacher/:teacherId/hourly', async (req, res) => {
  try {
    const { teacherId } = req.params;
    const { start, end } = validateDateParams(req.query.start as string, req.query.end as string);

    const hourlyData = await hourlyMessageHistogram(teacherId, start, end);

    // Fill in missing hours with 0 counts
    const completeHourlyData = Array.from({ length: 24 }, (_, hour) => {
      const existingData = hourlyData.find(d => d.hour === hour);
      return {
        hour,
        messageCount: existingData?.messageCount || 0
      };
    });

    const response = {
      teacherId,
      dateRange: {
        start: start.toISOString(),
        end: end.toISOString()
      },
      hourlyDistribution: completeHourlyData,
      summary: {
        totalMessages: completeHourlyData.reduce((sum, h) => sum + h.messageCount, 0),
        peakHour: completeHourlyData.reduce((peak, current) => 
          current.messageCount > peak.messageCount ? current : peak
        ),
        activeHours: completeHourlyData.filter(h => h.messageCount > 0).length
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Error in /teacher/:teacherId/hourly:', error);
    res.status(400).json({
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

/**
 * GET /teacher/:teacherId/faqs
 * Returns top FAQs and misconceptions for a teacher's cohort
 */
router.get('/teacher/:teacherId/faqs', async (req, res) => {
  try {
    const { teacherId } = req.params;
    const { start, end } = validateDateParams(req.query.start as string, req.query.end as string);
    const limit = parseInt(req.query.limit as string) || 10;

    if (limit < 1 || limit > 50) {
      return res.status(400).json({
        error: 'Limit must be between 1 and 50'
      });
    }

    const [faqData, misconceptions] = await Promise.all([
      topFaqs(teacherId, start, end, limit),
      misconceptionsByType(teacherId, start, end)
    ]);

    // Group FAQs by category
    const faqsByCategory = faqData.reduce((acc, faq) => {
      if (!acc[faq.category]) {
        acc[faq.category] = [];
      }
      acc[faq.category].push({
        question: faq.questionText,
        frequency: faq.frequencyCount,
        successRate: faq.successRate ? Math.round(faq.successRate * 100) : null
      });
      return acc;
    }, {} as Record<string, any[]>);

    const response = {
      teacherId,
      dateRange: {
        start: start.toISOString(),
        end: end.toISOString()
      },
      topFaqs: faqData.map(faq => ({
        question: faq.questionText,
        category: faq.category,
        frequency: faq.frequencyCount,
        successRate: faq.successRate ? Math.round(faq.successRate * 100) : null
      })),
      faqsByCategory,
      misconceptions: misconceptions.map(m => ({
        category: m.category,
        frequency: m.frequency,
        commonIssues: m.commonMisconceptions.slice(0, 5)
      })),
      summary: {
        totalFaqs: faqData.length,
        categoriesCount: Object.keys(faqsByCategory).length,
        avgSuccessRate: faqData.length > 0 ? 
          Math.round(faqData.filter(f => f.successRate !== null)
            .reduce((sum, f) => sum + (f.successRate || 0), 0) / 
            faqData.filter(f => f.successRate !== null).length * 100) : null
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Error in /teacher/:teacherId/faqs:', error);
    res.status(400).json({
      error: error instanceof Error ? error.message : 'Unknown error occurred'
    });
  }
});

/**
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    timestamp: new Date().toISOString(),
    service: 'analytics-api'
  });
});

export default router;
