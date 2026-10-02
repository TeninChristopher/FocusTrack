import { api, API_BASE_URL, USE_MOCK, mockDelay } from './api';
import logsMock from '@/mock/logs.json';
import sessionsMock from '@/mock/sessions.json';

/**
 * Logs domain service. Maps to routes/logs_routes.py:
 *   GET /api/logs?date=YYYY-MM-DD&limit=100
 *   GET /api/sessions
 *   GET /api/video/{session_id}
 */
export const logsService = {
  /** @param {string|null} date - YYYY-MM-DD, matches logs_routes.get_logs's `date` query param */
  async getLogs(date = null, limit = 100) {
    if (USE_MOCK) {
      const filtered = date ? logsMock.filter((l) => l.timestamp?.startsWith(date)) : logsMock;
      return mockDelay(filtered.slice(0, limit));
    }
    return api.get('/api/logs', { params: { date: date || undefined, limit } });
  },

  async getSessions() {
    if (USE_MOCK) return mockDelay(sessionsMock);
    return api.get('/api/sessions');
  },

  /**
   * Builds the streaming URL for a session's video -- GET /api/video/{session_id}
   * returns the raw video file (FileResponse in logs_routes.py), so this is a
   * direct URL for a <video> element's src, not a fetch() call.
   */
  getVideoUrl(sessionId) {
    return `${API_BASE_URL}/api/video/${sessionId}`;
  },
};
