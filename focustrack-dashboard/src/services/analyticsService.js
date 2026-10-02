import { api, USE_MOCK, mockDelay } from './api';
import analyticsMock from '@/mock/analytics.json';

/**
 * Analytics domain service. Maps to routes/analytics_routes.py:
 *   GET /api/analytics
 * Backend shape (analytics_service.get_analytics_summary): { dailyTrend, periodWise }.
 */
export const analyticsService = {
  async getAnalytics() {
    if (USE_MOCK) return mockDelay(analyticsMock);
    return api.get('/api/analytics');
  },
};
