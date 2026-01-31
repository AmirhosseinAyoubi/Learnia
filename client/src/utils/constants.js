/**
 * Application Constants
 */

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/v1/auth/me',
  },
  COURSES: {
    BASE: '/api/v1/courses',
    ENROLL: (id) => `/api/v1/courses/${id}/enroll`,
  },
  DOCUMENTS: {
    BASE: '/api/v1/documents',
    BY_ID: (id) => `/api/v1/documents/${id}`,
  },
  QUESTIONS: {
    BASE: '/api/v1/questions',
    BY_ID: (id) => `/api/v1/questions/${id}`,
    UPVOTE: (id) => `/api/v1/questions/${id}/upvote`,
  },
  QUIZZES: {
    BASE: '/api/v1/quizzes',
    BY_ID: (id) => `/api/v1/quizzes/${id}`,
    ATTEMPTS: (id) => `/api/v1/quizzes/${id}/attempts`,
  },
  CONTENT: {
    SEARCH: '/api/v1/content/chunks',
  },
}

export const USER_ROLES = {
  STUDENT: 'STUDENT',
  INSTRUCTOR: 'INSTRUCTOR',
  ADMIN: 'ADMIN',
}

export const DOCUMENT_TYPES = {
  PDF: 'PDF',
  PPTX: 'PPTX',
  TXT: 'TXT',
}

export const QUIZ_DIFFICULTY = {
  EASY: 'EASY',
  MEDIUM: 'MEDIUM',
  HARD: 'HARD',
}
