import { User } from 'lucide-react';
import { StatusBadge } from '@/components/common/StatusBadge';
import { attentionTone } from '@/utils/format';
import { cn } from '@/utils/cn';

/**
 * One student's live attention reading.
 * Reads fields exactly as returned by GET /api/status's `students[]`:
 * id, attention_score, attention_status, posture.
 */
export function StudentCard({ id, attention_score, attention_status, posture }) {
  const tone = attentionTone(attention_score);
  const ringColor = {
    success: 'ring-success-500/30 text-success-600 bg-success-500/10',
    warning: 'ring-warning-500/30 text-warning-600 bg-warning-500/10',
    danger: 'ring-danger-500/30 text-danger-600 bg-danger-500/10',
  }[tone];

  return (
    <div className="flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50">
      <div className={cn('flex h-9 w-9 shrink-0 items-center justify-center rounded-full ring-2', ringColor)}>
        <User className="h-4 w-4" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="font-data text-sm font-semibold text-slate-700 dark:text-slate-200">{id}</span>
          <span className="font-data text-xs text-slate-400">{attention_score}%</span>
        </div>
        {posture && <p className="truncate text-xs text-slate-400">{posture}</p>}
      </div>
      <StatusBadge status={attention_status} tone={tone} className="shrink-0" />
    </div>
  );
}
