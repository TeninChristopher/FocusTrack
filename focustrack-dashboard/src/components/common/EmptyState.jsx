import { Inbox } from 'lucide-react';

export function EmptyState({ icon: Icon = Inbox, title = 'Nothing here yet', description }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-slate-100 text-slate-400 dark:bg-slate-800">
        <Icon className="h-5 w-5" />
      </div>
      <p className="text-sm font-semibold text-slate-600 dark:text-slate-300">{title}</p>
      {description && <p className="max-w-xs text-xs text-slate-400">{description}</p>}
    </div>
  );
}
