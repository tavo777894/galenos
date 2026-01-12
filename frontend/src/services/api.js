import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  getCurrentUser: async () => {
    // This would need to be implemented in the backend
    // For now, we'll decode the JWT or return cached user
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};

// Patients API
export const patientsAPI = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/patients/', {
      params: { skip, limit },
    });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/patients/${id}`);
    return response.data;
  },

  create: async (patientData) => {
    const response = await api.post('/patients/', patientData);
    return response.data;
  },

  update: async (id, patientData) => {
    const response = await api.put(`/patients/${id}`, patientData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/patients/${id}`);
    return response.data;
  },

  searchByCI: async (ci) => {
    const response = await api.get(`/patients/search/ci/${ci}`);
    return response.data;
  },

  generateCard: async (id) => {
    const response = await api.post(`/patients/${id}/generate-card`);
    return response.data;
  },

  downloadCard: async (id) => {
    const response = await api.get(`/patients/${id}/card-pdf`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  getAll: async (patientId = null, documentType = null, skip = 0, limit = 100) => {
    const params = { skip, limit };
    if (patientId) params.patient_id = patientId;
    if (documentType) params.document_type = documentType;

    const response = await api.get('/documents/', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  download: async (id) => {
    const response = await api.get(`/documents/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  preview: async (id) => {
    const response = await api.get(`/documents/${id}/preview`, {
      responseType: 'blob',
    });
    return response.data;
  },

  reprint: async (id) => {
    const response = await api.post(`/documents/${id}/reprint`, null, {
      responseType: 'blob',
    });
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  },
};

// Search API
export const searchAPI = {
  globalSearch: async (query, limit = 10) => {
    const response = await api.get('/search', {
      params: { q: query, limit },
    });
    return response.data;
  },
};

export default api;
