import axios from 'axios';

/**
 * Base Axios client for the FocusTrack FastAPI backend.
 *
 * Points at VITE_API_URL (see .env.example), matching main.py's
 * uvicorn host:port exactly -- default http://localhost:8000. Routes
 * called from services are relative to this (e.g. api.get('/api/status')),
 * mirroring routes/analytics_routes.py, routes/logs_routes.py verbatim.
 *
 * VITE_USE_MOCK controls whether services resolve from local mock JSON
 * (default, so the UI runs standalone before/without the backend running)
 * or hit the real API through this client. Flip it once FastAPI is
 * running locally -- no component code needs to change.
 */
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Network error';
    return Promise.reject(new Error(message));
  }
);

/** Simulates realistic network latency for mock responses during development. */
export function mockDelay(data, ms = 300) {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}
