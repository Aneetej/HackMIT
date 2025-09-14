import api from '../axios-config';

// TypeScript interfaces for registration
export interface StudentRegistrationData {
  email: string;
  name: string;
  grade: string;
  subject_focus?: string;
  learning_style?: string;
}

export interface TeacherRegistrationData {
  email: string;
  name: string;
  subject: string;
}

export interface StudentRegistrationResponse {
  success: boolean;
  studentId: string;
  student: {
    id: string;
    name: string;
    email: string;
    grade: number;
    subject_focus: string;
    learning_style: string;
  };
}

export interface TeacherRegistrationResponse {
  success: boolean;
  teacherId: string;
  teacher: {
    id: string;
    name: string;
    email: string;
    subject: string;
  };
}

export interface StudentSignInData {
  email: string;
}

export interface TeacherSignInData {
  email: string;
}

export interface StudentSignInResponse {
  success: boolean;
  studentId: string;
  student: {
    id: string;
    name: string;
    email: string;
    grade: number;
    subject_focus: string;
    learning_style: string;
  };
}

export interface TeacherSignInResponse {
  success: boolean;
  teacherId: string;
  teacher: {
    id: string;
    name: string;
    email: string;
    subject: string;
  };
}

// API Functions
export const authApi = {
  // Register new student
  registerStudent: async (data: StudentRegistrationData): Promise<StudentRegistrationResponse> => {
    const response = await api.post('/api/student/register', data);
    return response.data;
  },

  // Register new teacher
  registerTeacher: async (data: TeacherRegistrationData): Promise<TeacherRegistrationResponse> => {
    const response = await api.post('/api/teacher/register', data);
    return response.data;
  },

  // Sign in student
  signInStudent: async (data: StudentSignInData): Promise<StudentSignInResponse> => {
    const response = await api.post('/api/student/signin', data);
    return response.data;
  },

  // Sign in teacher
  signInTeacher: async (data: TeacherSignInData): Promise<TeacherSignInResponse> => {
    const response = await api.post('/api/teacher/signin', data);
    return response.data;
  }
};
