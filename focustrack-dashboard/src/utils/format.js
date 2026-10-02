/** Shared formatting helpers, kept consistent with the backend's own status/threshold logic. */

export function formatPercent(value) {
  if (value === null || value === undefined) return '--';
  return `${Math.round(value)}%`;
}

export function formatRelativeTime(isoString) {
  if (!isoString) return '--';
  const diffMs = Date.now() - new Date(isoString).getTime();
  const diffSec = Math.max(0, Math.round(diffMs / 1000));
  if (diffSec < 60) return `${diffSec} sec ago`;
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin} min ago`;
  const diffHr = Math.round(diffMin / 60);
  return `${diffHr} hr ago`;
}

export function formatDate(dateString) {
  if (!dateString) return '--';
  return new Date(dateString).toLocaleDateString(undefined, {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

/**
 * Attention score -> semantic status/tone. Mirrors the backend's own bands
 * exactly (utils/config.py: ATTENTION_HIGH_THRESHOLD=80, ATTENTION_PARTIAL_THRESHOLD=55),
 * so the frontend never disagrees with the status string the API already sends.
 */
export function attentionTone(score) {
  if (score === null || score === undefined) return 'neutral';
  if (score >= 80) return 'success';
  if (score >= 55) return 'warning';
  return 'danger';
}

/** Maps a backend attention_status string (or stats.systemStatus etc) to a badge tone. */
export function statusTone(status) {
  const s = (status || '').toLowerCase();
  if (['highly attentive', 'online', 'running', 'connected'].includes(s)) return 'success';
  if (['partially attentive', 'idle'].includes(s)) return 'warning';
  if (['distracted', 'offline', 'error'].includes(s)) return 'danger';
  return 'neutral';
}
