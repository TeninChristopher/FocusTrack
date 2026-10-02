import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function ErrorState({ message = 'Failed to load data.', onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-center">
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-danger-500/10 text-danger-500">
        <AlertTriangle className="h-5 w-5" />
      </div>
      <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Retry
        </Button>
      )}
    </div>
  );
}
