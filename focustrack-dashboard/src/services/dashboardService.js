import { api, API_BASE_URL, USE_MOCK, mockDelay } from './api';
import dashboardMock from '@/mock/dashboard.json';
import deviceStatusMock from '@/mock/deviceStatus.json';

/**
 * Dashboard domain service. Maps directly to routes/analytics_routes.py:
 *   GET /api/status
 *   GET /api/device-status
 */
export const dashboardService = {
  /** Full live snapshot: students, stats, device. See analytics_routes.get_status. */
  async getStatus() {
    if (USE_MOCK) return mockDelay(dashboardMock);
    return api.get('/api/status');
  },

  /** ESP32-CAM / backend / storage health + active track count. See analytics_routes.get_device_status. */
  async getDeviceStatus() {
    if (USE_MOCK) return mockDelay(deviceStatusMock);
    return api.get('/api/device-status');
  },

  /**
   * URL for the latest annotated classroom frame.
   *
   * NOTE: the current backend (routes/image_routes.py, services/image_service.py)
   * saves annotated frames to uploads/processed/ but does not yet expose a route
   * to fetch the *latest* one -- only GET /api/video/{session_id} for a full
   * recorded session. This builds the natural URL for when that route exists
   * (e.g. StaticFiles mount at /uploads or a dedicated GET /api/frame/latest);
   * until then LiveMonitoringCard falls back to its simulated overlay.
   */
  getLatestFrameUrl() {
    return `${API_BASE_URL}/uploads/processed/latest.jpg`;
  },
};
