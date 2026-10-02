import { ArrowDown, EyeOff, TrendingDown } from 'lucide-react';
import { EmptyState } from '@/components/common/EmptyState';

/**
 * Reads GET /api/logs entries exactly as shaped by
 * services/analytics_service.evaluate_and_log_events:
 *   Attention Drop: { time, studentId, type, from, to, reason }
 *   Eyes Closed:    { time, studentId, type, duration }
 */
export function LogsTimeline({ logs = [] }) {
  if (logs.length === 0) {
    return <EmptyState title="No events logged" description="No attention events for this date." />;
  }

  return (
    <ol className="relative space-y-6 pl-6">
      <div className="absolute bottom-2 left-[7px] top-2 w-px bg-slate-200 dark:bg-slate-800" />
      {logs.map((log) => {
        const isDrop = log.type === 'Attention Drop';
        return (
          <li key={log.id} className="relative">
            <span
              className={`absolute -left-6 top-1 flex h-3.5 w-3.5 items-center justify-center rounded-full ring-4 ring-white dark:ring-[#111a2c] ${
                isDrop ? 'bg-danger-500' : 'bg-warning-500'
              }`}
            />
            <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="font-data font-semibold text-slate-500 dark:text-slate-400">{log.time}</span>
              <span className="font-data rounded bg-slate-100 px-1.5 py-0.5 font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {log.studentId}
              </span>
              <span className="text-slate-400">{log.type}</span>
            </div>

            {isDrop ? (
              <div className="mt-1 flex items-center gap-2 text-sm">
                <TrendingDown className="h-4 w-4 text-danger-500" />
                <span className="font-data font-semibold text-slate-700 dark:text-slate-200">{log.from}%</span>
                <ArrowDown className="h-3 w-3 text-slate-300" />
                <span className="font-data font-semibold text-danger-500">{log.to}%</span>
                <span className="text-slate-400">&middot; Reason: {log.reason}</span>
              </div>
            ) : (
              <div className="mt-1 flex items-center gap-2 text-sm">
                <EyeOff className="h-4 w-4 text-warning-500" />
                <span className="font-medium text-slate-700 dark:text-slate-200">Eyes Closed</span>
                <span className="text-slate-400">&middot; Duration: {log.duration}</span>
              </div>
            )}
          </li>
        );
      })}
    </ol>
  );
}
