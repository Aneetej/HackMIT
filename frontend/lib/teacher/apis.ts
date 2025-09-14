import api from '../axios-config';

// TypeScript interfaces for API responses
export interface ClassData {
  id: string;
  name: string;
  restrictions?: string;
  teachingStyle?: string;
  studentGrade?: string;
  subject?: string;
  otherNotes?: string;
  teacherId: string;
  studentCount?: number;
}

export interface CreateClassRequest {
  name: string;
  restrictions?: string;
  teachingStyle?: string;
  studentGrade?: string;
  subject?: string;
  otherNotes?: string;
}

export interface UpdateClassRequest {
  name?: string;
  restrictions?: string;
  teachingStyle?: string;
  studentGrade?: string;
  subject?: string;
  otherNotes?: string;
}

export interface StudentData {
  id: string;
  name: string;
  email: string;
  grade: number;
  subject_focus: string;
  learning_style: string;
  preferred_content: string;
  created_at: string;
  sessionInfo?: {
    id: string;
    questions_asked: number;
    started_at: string;
    ended_at?: string;
    status: string;
  };
}

export interface MessageInsightsData {
  averageMessagesPerStudent: number;
  totalStudents: number;
  totalMessages: number;
  studentBreakdown: {
    studentId: string;
    studentName: string;
    messageCount: number;
  }[];
  dateRange: {
    from: string;
    to: string;
  };
}

export interface StudentDailyUsageData {
  studentId: string;
  studentName: string;
  classId: string;
  dailyUsage: {
    day: string;
    date: string;
    messageCount: number;
    messages: {
      id: string;
      timestamp: string;
      content: string;
    }[];
  }[];
  totalMessages: number;
  averageDailyMessages: number;
  dateRange: {
    from: string;
    to: string;
  };
}

export interface InsightData {
  id: string;
  title: string;
  description: string;
  classId: string;
}

export interface CreateInsightRequest {
  title: string;
  description: string;
}

export interface UpdateInsightRequest {
  title: string;
  description: string;
}

export interface NoteData {
  id: string;
  content: string;
  classId: string;
  studentId: string;
}

export interface UpdateNoteRequest {
  content: string;
}

// API Functions
export const teacherApi = {
  // Create a new class
  createClass: async (teacherId: string, classData: CreateClassRequest): Promise<{ success: boolean; class: ClassData }> => {
    const response = await api.post(`/api/teacher/${teacherId}/class`, classData);
    return response.data;
  },

  // Get all classes for a teacher
  getClasses: async (teacherId: string): Promise<{ success: boolean; classes: ClassData[] }> => {
    const response = await api.get(`/api/teacher/${teacherId}/classes`);
    return response.data;
  },

  // Get a single class by ID
  getClass: async (classId: string): Promise<{ success: boolean; class: ClassData }> => {
    const response = await api.get(`/api/class/${classId}`);
    return response.data;
  },

  // Update class details
  updateClass: async (classId: string, classData: UpdateClassRequest): Promise<{ success: boolean; class: ClassData }> => {
    const response = await api.put(`/api/class/${classId}`, classData);
    return response.data;
  },

  // Delete a class
  deleteClass: async (classId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/api/class/${classId}`);
    return response.data;
  },

  // Get all students for a specific class
  getClassStudents: async (classId: string): Promise<{ success: boolean; students: StudentData[] }> => {
    const response = await api.get(`/api/class/${classId}/students`);
    return response.data;
  },

  // Get message insights for a specific class
  getMessageInsights: async (classId: string): Promise<{ success: boolean; data: MessageInsightsData }> => {
    const response = await api.get(`/api/class/${classId}/insights/messages`);
    return response.data;
  },

  // Get daily usage for a specific student in a class
  getStudentDailyUsage: async (classId: string, studentId: string): Promise<{ success: boolean; data: StudentDailyUsageData }> => {
    const response = await api.get(`/api/class/${classId}/student/${studentId}/daily-usage`);
    return response.data;
  },

  // Insight management functions
  
  // Create a new insight for a class
  createInsight: async (classId: string, insightData: CreateInsightRequest): Promise<{ success: boolean; insight: InsightData }> => {
    const response = await api.post(`/api/classes/${classId}/insights`, insightData);
    return response.data;
  },

  // Get all insights for a class
  getInsights: async (classId: string): Promise<{ success: boolean; insights: InsightData[] }> => {
    const response = await api.get(`/api/classes/${classId}/insights`);
    return response.data;
  },

  // Update an existing insight
  updateInsight: async (insightId: string, insightData: UpdateInsightRequest): Promise<{ success: boolean; insight: InsightData }> => {
    const response = await api.put(`/api/insights/${insightId}`, insightData);
    return response.data;
  },

  // Delete an insight
  deleteInsight: async (insightId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/api/insights/${insightId}`);
    return response.data;
  },

  // Note management functions
  
  // Get note for a student in a class (creates empty note if none exists)
  getNote: async (classId: string, studentId: string): Promise<{ success: boolean; note: NoteData }> => {
    const response = await api.get(`/api/classes/${classId}/students/${studentId}/note`);
    return response.data;
  },

  // Update note for a student in a class
  updateNote: async (classId: string, studentId: string, noteData: UpdateNoteRequest): Promise<{ success: boolean; note: NoteData }> => {
    const response = await api.put(`/api/classes/${classId}/students/${studentId}/note`, noteData);
    return response.data;
  }
};
