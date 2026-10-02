import { Calendar, RotateCcw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * Date picker for filtering GET /api/logs?date=YYYY-MM-DD, plus a
 * refresh action. Clearing the date goes back to the unfiltered feed.
 */
export function DateFilter({ date, onChange, onRefresh }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <label className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm dark:border-slate-800 dark:bg-[#111a2c]">
        <Calendar className="h-4 w-4 text-slate-400" />
        <input
          type="date"
          value={date || ''}
          onChange={(e) => onChange(e.target.value || null)}
          className="bg-transparent font-data text-sm text-slate-700 focus:outline-none dark:text-slate-200"
        />
      </label>

      {date && (
        <Button variant="ghost" size="icon" onClick={() => onChange(null)} aria-label="Clear date filter">
          <X className="h-4 w-4" />
        </Button>
      )}

      <Button variant="outline" size="sm" onClick={onRefresh}>
        <RotateCcw className="h-3.5 w-3.5" />
        Refresh
      </Button>
    </div>
  );
}
