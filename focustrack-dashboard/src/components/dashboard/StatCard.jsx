import { cn } from '@/utils/cn';

const toneClasses = {
  brand: 'text-brand-600 bg-brand-500/10 dark:text-brand-400',
  success: 'text-success-600 bg-success-500/10 dark:text-success-500',
  warning: 'text-warning-600 bg-warning-500/10 dark:text-warning-500',
  danger: 'text-danger-600 bg-danger-500/10 dark:text-danger-500',
};

export function StatCard({ icon: Icon, label, value, suffix, tone = 'brand' }) {
  return (
    <div className="card-surface flex items-center gap-4 p-5">
      <div className={cn('flex h-11 w-11 shrink-0 items-center justify-center rounded-xl', toneClasses[tone])}>
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0">
        <p className="truncate text-xs font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <p className="font-data text-2xl font-bold text-slate-900 dark:text-white">
          {value}
          {suffix && <span className="ml-0.5 text-base font-semibold text-slate-400">{suffix}</span>}
        </p>
      </div>
    </div>
  );
}
