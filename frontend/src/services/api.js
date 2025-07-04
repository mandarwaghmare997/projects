// API service for Qryti Learn frontend-backend communication
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.qryti.com' 
  : 'http://localhost:5002';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get current token from localStorage
  get token() {
    return localStorage.getItem('access_token');
  }

  // Set authentication token
  setToken(token) {
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  // Get authentication headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(options.auth !== false),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        // Handle token expiration
        if (response.status === 401 && this.token) {
          await this.refreshToken();
          // Retry the request with new token
          config.headers = this.getHeaders(options.auth !== false);
          const retryResponse = await fetch(url, config);
          if (retryResponse.ok) {
            return await retryResponse.json();
          }
        }
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication methods
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      auth: false,
    });
  }

  async login(credentials) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
      auth: false,
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
    }

    return response;
  }

  async logout() {
    try {
      await this.request('/api/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
      localStorage.removeItem('refresh_token');
    }
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      // Make direct fetch request to avoid circular dependency
      const response = await fetch(`${this.baseURL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Token refresh failed');
      }

      if (data.access_token) {
        this.setToken(data.access_token);
      }

      return data;
    } catch (error) {
      // Refresh failed, clear tokens
      this.setToken(null);
      localStorage.removeItem('refresh_token');
      throw error;
    }
  }

  async getProfile() {
    return this.request('/api/auth/profile');
  }

  async updateProfile(profileData) {
    return this.request('/api/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData) {
    return this.request('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  // Course methods
  async getCourses(level = null) {
    const query = level ? `?level=${level}` : '';
    return this.request(`/api/courses/${query}`, { auth: false });
  }

  async getCourse(courseId) {
    return this.request(`/api/courses/${courseId}`, { auth: false });
  }

  async getCourseModules(courseId) {
    return this.request(`/api/courses/${courseId}/modules`, { auth: false });
  }

  async enrollInCourse(courseId) {
    return this.request(`/api/courses/${courseId}/enroll`, {
      method: 'POST',
    });
  }

  async unenrollFromCourse(courseId) {
    return this.request(`/api/courses/${courseId}/unenroll`, {
      method: 'DELETE',
    });
  }

  async getMyCourses() {
    return this.request('/api/courses/my-courses');
  }

  async getCourseProgress(courseId) {
    return this.request(`/api/courses/${courseId}/progress`);
  }

  async getModule(moduleId) {
    return this.request(`/api/courses/modules/${moduleId}`);
  }

  async completeModule(moduleId, data = {}) {
    return this.request(`/api/courses/modules/${moduleId}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Quiz methods
  async getAllQuizzes() {
    return this.request('/api/quizzes/', { auth: false });
  }

  async getCourseQuizzes(courseId) {
    return this.request(`/api/courses/${courseId}/quizzes`, { auth: false });
  }

  async getModuleQuizzes(moduleId) {
    return this.request(`/api/quizzes/module/${moduleId}`);
  }

  async getQuiz(quizId) {
    return this.request(`/api/quizzes/${quizId}`);
  }

  async startQuiz(quizId) {
    return this.request(`/api/quizzes/${quizId}/start`, {
      method: 'POST',
    });
  }

  async submitQuizAttempt(quizId, attemptData) {
    return this.request(`/api/quizzes/${quizId}/submit`, {
      method: 'POST',
      body: JSON.stringify(attemptData),
    });
  }

  async submitQuiz(attemptId, answers) {
    return this.request(`/api/quizzes/attempts/${attemptId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  }

  async getQuizResults(attemptId) {
    return this.request(`/api/quizzes/attempts/${attemptId}/results`);
  }

  async getUserQuizAttempts() {
    return this.request('/api/quizzes/my-attempts');
  }

  async getMyQuizAttempts() {
    return this.request('/api/quizzes/my-attempts');
  }

  // Progress methods
  async getDashboard() {
    return this.request('/api/progress/dashboard');
  }

  async getProgressStats() {
    return this.request('/api/progress/stats');
  }

  async getLearningAnalytics(days = 30, eventType = null) {
    const params = new URLSearchParams({ days: days.toString() });
    if (eventType) params.append('event_type', eventType);
    return this.request(`/api/progress/analytics?${params}`);
  }

  async updateTimeSpent(moduleId, minutes) {
    return this.request(`/api/progress/module/${moduleId}/time`, {
      method: 'POST',
      body: JSON.stringify({ minutes }),
    });
  }

  // Certificate methods
  async getMyCertificates() {
    return this.request('/api/certificates/my-certificates');
  }

  async generateCertificate(courseId) {
    return this.request(`/api/certificates/generate/${courseId}`, {
      method: 'POST',
    });
  }

  async getCertificate(certificateId) {
    return this.request(`/api/certificates/${certificateId}`, { auth: false });
  }

  async verifyCertificate(certificateId) {
    return this.request(`/api/certificates/verify/${certificateId}`, { auth: false });
  }

  async verifyCertificateByCode(verificationCode) {
    return this.request('/api/certificates/verify-code', {
      method: 'POST',
      body: JSON.stringify({ verification_code: verificationCode }),
      auth: false,
    });
  }

  async checkCertificateEligibility(courseId) {
    return this.request(`/api/certificates/course/${courseId}/eligible`);
  }

  // Statistics methods
  async getCourseStats() {
    return this.request('/api/courses/stats', { auth: false });
  }

  async getCertificateStats() {
    return this.request('/api/certificates/stats', { auth: false });
  }

  // Health check
  async healthCheck() {
    return this.request('/health', { auth: false });
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // Get current user from token (basic decode)
  getCurrentUser() {
    if (!this.token) return null;
    
    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      return payload;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;

