import { cn } from '@/utils/cn';

export function LoadingSkeleton({ className, rows = 1 }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className={cn('animate-pulse rounded-lg bg-slate-200/70 dark:bg-slate-800/70', className)} />
      ))}
    </div>
  );
}

export function CardSkeleton({ className }) {
  return (
    <div className={cn('card-surface p-5', className)}>
      <LoadingSkeleton className="mb-4 h-4 w-24" />
      <LoadingSkeleton className="h-8 w-16" />
    </div>
  );
}
