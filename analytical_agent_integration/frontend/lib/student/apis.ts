import api from '../axios-config';

// TypeScript interfaces for API responses
export interface ChatMessage {
  id: string;
  message: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}

export interface ClassInfo {
  id: string;
  name: string;
  teacherName?: string;
  studentCount?: number;
  restrictions?: string;
  teachingStyle?: string;
  studentGrade?: string;
  subject?: string;
  otherNotes?: string;
}

export interface StudentInfo {
  interests: string;
  learningStyle: string;
  classes: ClassInfo[];
}

export interface JoinClassResponse {
  success: boolean;
  message: string;
  classTitle: string;
  chatSessionId: string;
}

export interface GetClassesResponse {
  success: boolean;
  classes: ClassInfo[];
}

export interface ClassDetails {
  classId: string;
  className: string;
  chatHistory: ChatMessage[];
}

export interface MessageResponse {
  id: string;
  message: string;
  sender: 'assistant';
  timestamp: string;
}

// API Functions
export const studentApi = {
  // Get student info and enrolled classes
  getStudentInfo: async (studentId: string): Promise<StudentInfo> => {
    const response = await api.get(`/api/student/${studentId}`);
    return response.data;
  },

  // Get class details and chat history
  getClass: async (studentId: string, classId: string): Promise<ClassDetails> => {
    const response = await api.get(`/api/student/${studentId}/class/${classId}`);
    return response.data;
  },

  // Send message and get AI response
  sendMessage: async (studentId: string, classId: string, message: string): Promise<MessageResponse> => {
    const response = await api.post(`/api/student/${studentId}/class/${classId}/message`, {
      message
    });
    return response.data;
  },

  // Join a class by class ID
  joinClass: async (classId: string, studentId: string): Promise<JoinClassResponse> => {
    const response = await api.post('/api/student/join-class', {
      classId,
      studentId
    });
    return response.data;
  },

  // Get all classes for a student
  getClasses: async (studentId: string): Promise<GetClassesResponse> => {
    const response = await api.get(`/api/student/${studentId}/classes`);
    return response.data;
  },

  // Update student preferences
  updatePreferences: async (studentId: string, interests: string, learningStyle: string): Promise<{ success: boolean }> => {
    const response = await api.put(`/api/student/${studentId}/preferences`, {
      interests,
      learningStyle
    });
    return response.data;
  }
}; 

