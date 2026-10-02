import { cn } from '@/utils/cn';
import { statusTone } from '@/utils/format';

const toneClasses = {
  success: 'bg-success-500/10 text-success-600 dark:text-success-500',
  warning: 'bg-warning-500/10 text-warning-600 dark:text-warning-500',
  danger: 'bg-danger-500/10 text-danger-600 dark:text-danger-500',
  neutral: 'bg-slate-500/10 text-slate-600 dark:text-slate-400',
};

const dotClasses = {
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  danger: 'bg-danger-500',
  neutral: 'bg-slate-400',
};

/**
 * Renders a status string (e.g. "Online", "Highly Attentive", "Offline")
 * with an auto-derived color tone, so every status pill across the app
 * (device status, attention status, system status) looks consistent.
 * Pass `tone` explicitly to override the auto-detected mapping.
 */
export function StatusBadge({ status, tone, pulse = false, className }) {
  const resolvedTone = tone || statusTone(status);

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold',
        toneClasses[resolvedTone],
        className
      )}
    >
      <span className="relative flex h-1.5 w-1.5">
        {pulse && (
          <span
            className={cn('absolute inline-flex h-full w-full animate-ping rounded-full opacity-60', dotClasses[resolvedTone])}
          />
        )}
        <span className={cn('relative inline-flex h-1.5 w-1.5 rounded-full', dotClasses[resolvedTone])} />
      </span>
      {status}
    </span>
  );
}
