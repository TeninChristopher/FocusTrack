import { Play } from 'lucide-react';
import { formatDate } from '@/utils/format';

/**
 * Reads GET /api/sessions entries exactly:
 * { id, date, video_file, frame_count, started_at, updated_at }.
 * onSelect(sessionId) triggers VideoPlayer to load GET /api/video/{session_id}.
 */
export function RecordingCard({ id, date, frame_count, onSelect, active }) {
  return (
    <button
      type="button"
      onClick={() => onSelect(id)}
      className={`group flex w-full items-center gap-4 rounded-xl border p-3 text-left transition-colors ${
        active
          ? 'border-brand-300 bg-brand-50 dark:border-brand-500/40 dark:bg-brand-500/10'
          : 'border-slate-100 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50'
      }`}
    >
      <div className="flex h-16 w-24 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 transition-transform group-hover:scale-105">
        <Play className="h-5 w-5 fill-white text-white" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-200">{formatDate(date)}</p>
        <p className="text-xs text-slate-400">Session {id.replace('session_', '')}</p>
      </div>
      {frame_count !== undefined && (
        <div className="shrink-0 text-right">
          <p className="font-data text-sm font-bold text-brand-600 dark:text-brand-400">{frame_count}</p>
          <p className="text-[10px] uppercase tracking-wide text-slate-400">frames</p>
        </div>
      )}
    </button>
  );
}
