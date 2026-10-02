import { useCallback, useEffect, useState } from 'react';
import { analyticsService } from '@/services/analyticsService';

/** Drives the Analytics page: fetches GET /api/analytics once, with a manual refresh. */
export function useAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyticsService.getAnalytics();
      setData(result);
    } catch (err) {
      setError(err?.message || 'Failed to load analytics.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { data, loading, error, refresh: load };
}
