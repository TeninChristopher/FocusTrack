import { useCallback, useEffect, useState } from 'react';
import { logsService } from '@/services/logsService';

/**
 * Drives the Logs page: GET /api/logs (with optional ?date=) and
 * GET /api/sessions, exposed as two independent loading/error pairs
 * since sessions rarely change while logs are date-filtered often.
 */
export function useLogs() {
  const [date, setDate] = useState(null);

  const [logs, setLogs] = useState(null);
  const [logsLoading, setLogsLoading] = useState(true);
  const [logsError, setLogsError] = useState(null);

  const [sessions, setSessions] = useState(null);
  const [sessionsLoading, setSessionsLoading] = useState(true);
  const [sessionsError, setSessionsError] = useState(null);

  const loadLogs = useCallback(async () => {
    setLogsLoading(true);
    setLogsError(null);
    try {
      const result = await logsService.getLogs(date, 100);
      setLogs(result);
    } catch (err) {
      setLogsError(err?.message || 'Failed to load logs.');
    } finally {
      setLogsLoading(false);
    }
  }, [date]);

  const loadSessions = useCallback(async () => {
    setSessionsLoading(true);
    setSessionsError(null);
    try {
      const result = await logsService.getSessions();
      setSessions(result);
    } catch (err) {
      setSessionsError(err?.message || 'Failed to load sessions.');
    } finally {
      setSessionsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  return {
    date,
    setDate,
    logs,
    logsLoading,
    logsError,
    refreshLogs: loadLogs,
    sessions,
    sessionsLoading,
    sessionsError,
    refreshSessions: loadSessions,
  };
}
