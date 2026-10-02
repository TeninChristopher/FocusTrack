import { DailyAttentionChart } from '@/components/analytics/DailyAttentionChart';
import { PeriodAttentionChart } from '@/components/analytics/PeriodAttentionChart';
import { CardSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { useAnalytics } from '@/hooks/useAnalytics';

export default function Analytics() {
  const { data, loading, error, refresh } = useAnalytics();

  if (loading) {
    return (
      <div className="grid gap-5 lg:grid-cols-2">
        <CardSkeleton className="h-80" />
        <CardSkeleton className="h-80" />
      </div>
    );
  }

  if (error) return <ErrorState message={error} onRetry={refresh} />;

  return (
    <div className="space-y-5 pb-16">
      <div>
        <h1 className="text-xl font-bold text-slate-900 dark:text-white">Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Attentiveness trends for Classroom A-101</p>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <DailyAttentionChart data={data?.dailyTrend || []} />
        <PeriodAttentionChart data={data?.periodWise || []} />
      </div>
    </div>
  );
}
