import { useCallback, useEffect, useRef, useState } from 'react';
import { dashboardService } from '@/services/dashboardService';

const POLL_INTERVAL_MS = 1500;

/**
 * Drives the Dashboard page: fetches + polls GET /api/status and
 * GET /api/device-status together, exposing a single loading/error state
 * and a manual refresh escape hatch.
 *
 * Polling keeps running in the background after the first successful
 * load -- a transient poll failure sets `error` for the UI to show, but
 * doesn't stop the interval, since the next poll may well succeed (e.g.
 * backend restarting, brief LAN hiccup between ESP32-CAM uploads).
 */
export function useDashboard() {
  const [status, setStatus] = useState(null);
  const [deviceStatus, setDeviceStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const load = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    try {
      const [statusResult, deviceResult] = await Promise.all([
        dashboardService.getStatus(),
        dashboardService.getDeviceStatus(),
      ]);
      setStatus(statusResult);
      setDeviceStatus(deviceResult);
      setError(null);
    } catch (err) {
      setError(err?.message || 'Failed to reach the backend.');
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(); // initial load shows the loading state

    intervalRef.current = setInterval(() => load({ silent: true }), POLL_INTERVAL_MS);
    return () => clearInterval(intervalRef.current);
  }, [load]);

  const refresh = useCallback(() => load(), [load]);

  return { status, deviceStatus, loading, error, refresh };
}
