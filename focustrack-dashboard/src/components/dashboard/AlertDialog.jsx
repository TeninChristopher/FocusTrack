import { useEffect, useState } from 'react';
import { Bell, TrendingDown, EyeOff } from 'lucide-react';
import { Dialog, DialogTrigger, DialogContent } from '@/components/ui/dialog';
import { EmptyState } from '@/components/common/EmptyState';
import { logsService } from '@/services/logsService';

/**
 * Floating alert button + dialog, populated from the same event log the
 * Logs page reads (GET /api/logs) -- "Attention Drop" and "Eyes Closed"
 * events double as alerts here, filtered to the most recent handful so
 * the button badge count stays meaningful rather than showing the full
 * day's history.
 */
export function AlertDialog() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    let cancelled = false;
    logsService
      .getLogs(null, 5)
      .then((logs) => {
        if (!cancelled) setAlerts(logs);
      })
      .catch(() => {
        if (!cancelled) setAlerts([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          aria-label={`${alerts.length} alerts`}
          className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-danger-500 text-white shadow-lg shadow-danger-500/30 transition-transform hover:scale-105 active:scale-95"
        >
          <Bell className="h-5 w-5" />
          {alerts.length > 0 && (
            <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-white px-1 font-data text-[11px] font-bold text-danger-600 ring-2 ring-danger-500">
              {alerts.length}
            </span>
          )}
        </button>
      </DialogTrigger>

      <DialogContent title="Recent Alerts">
        {alerts.length === 0 ? (
          <EmptyState title="No alerts" description="Everything looks calm in the classroom." />
        ) : (
          <ul className="max-h-80 space-y-1 overflow-y-auto scrollbar-thin">
            {alerts.map((alert) => {
              const isDrop = alert.type === 'Attention Drop';
              const Icon = isDrop ? TrendingDown : EyeOff;
              return (
                <li
                  key={alert.id}
                  className="flex items-start gap-3 border-b border-slate-100 py-3 last:border-0 dark:border-slate-800"
                >
                  <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-danger-500/10 text-danger-500">
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div>
                    <p className="font-data text-xs text-slate-400">{alert.time}</p>
                    <p className="text-sm text-slate-700 dark:text-slate-200">
                      {isDrop
                        ? `${alert.studentId} attention dropped from ${alert.from}% to ${alert.to}%`
                        : `${alert.studentId} eyes closed for ${alert.duration}`}
                    </p>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </DialogContent>
    </Dialog>
  );
}
