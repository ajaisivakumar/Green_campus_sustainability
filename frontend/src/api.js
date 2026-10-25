// API client — wraps all backend calls.
//
// LOCAL DEV:  Vite proxy forwards /api/* → http://127.0.0.1:8000  (no CORS issues)
// PRODUCTION: Set VITE_API_URL=https://your-backend.onrender.com in frontend env vars
//             and the axios baseURL switches automatically.

import axios from 'axios';

// In production (Render static site), VITE_API_URL points to the backend service.
// In local dev, baseURL '/api' is caught by the Vite proxy and forwarded to :8000.
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : '/api';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// Global error interceptor — logs API errors to console
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || 'Unknown error';
    console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url} → ${msg}`);
    return Promise.reject(error);
  }
);

export const healthAPI = {
  check: () => api.get('/health'),
};

export const buildingsAPI = {
  list: () => api.get('/buildings'),
  get: (id) => api.get(`/buildings/${id}`),
  create: (data) => api.post('/buildings', data),
  update: (id, data) => api.put(`/buildings/${id}`, data),
  delete: (id) => api.delete(`/buildings/${id}`),
};

export const datasetsAPI = {
  list: () => api.get('/datasets'),
  upload: (dataType, formData) =>
    api.post(`/datasets/upload/${dataType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  delete: (id) => api.delete(`/datasets/${id}`),
};

export const auditAPI = {
  list: () => api.get('/audit'),
  start: (data) => api.post('/audit/run', data),
  get: (runId) => api.get(`/audit/${runId}`),
  getAgents: (runId) => api.get(`/audit/${runId}/agents`),
  getFindings: (runId) => api.get(`/audit/${runId}/findings`),
};

export const analyticsAPI = {
  dashboard: () => api.get('/analytics/dashboard'),
  energy: (params) => api.get('/analytics/energy', { params }),
  water: (params) => api.get('/analytics/water', { params }),
  waste: (params) => api.get('/analytics/waste', { params }),
};

export const actionsAPI = {
  list: (params) => api.get('/actions', { params }),
  get: (id) => api.get(`/actions/${id}`),
  updateStatus: (id, data) => api.patch(`/actions/${id}/status`, data),
  getHistory: (id) => api.get(`/actions/${id}/history`),
};

export const verificationAPI = {
  run: (data) => api.post('/verification/run', data),
  get: (actionId) => api.get(`/verification/${actionId}`),
};

export const reportsAPI = {
  list: () => api.get('/reports'),
  generate: (runId, campusName) =>
    api.post(`/reports/generate/${runId}`, null, { params: { campus_name: campusName } }),
  download: (reportId) => window.open(`${BASE_URL}/reports/download/${reportId}`, '_blank'),
};

export const settingsAPI = {
  get: () => api.get('/settings'),
  update: (data) => api.patch('/settings', data),
};

export default api;
