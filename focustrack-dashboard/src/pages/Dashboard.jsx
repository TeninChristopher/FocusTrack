import { Users, Gauge, AlertCircle, ServerCog } from 'lucide-react';
import { StatCard } from '@/components/dashboard/StatCard';
import { LiveMonitoringCard } from '@/components/dashboard/LiveMonitoringCard';
import { StudentPanel } from '@/components/dashboard/StudentPanel';
import { DeviceStatusCard } from '@/components/dashboard/DeviceStatusCard';
import { AlertDialog } from '@/components/dashboard/AlertDialog';
import { CardSkeleton } from '@/components/common/LoadingSkeleton';
import { ErrorState } from '@/components/common/ErrorState';
import { useDashboard } from '@/hooks/useDashboard';
import { dashboardService } from '@/services/dashboardService';

export default function Dashboard() {
  const { status, deviceStatus, loading, error, refresh } = useDashboard();

  if (loading) {
    return (
      <div className="space-y-5">
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} className="h-16" />
          ))}
        </div>
        <CardSkeleton className="h-96" />
      </div>
    );
  }

  if (error && !status) {
    return <ErrorState message={error} onRetry={refresh} />;
  }

  const stats = status?.stats || {};
  const students = status?.students || [];

  return (
    <div className="space-y-5 pb-16">
      {error && (
        <div className="rounded-xl border border-warning-500/30 bg-warning-500/10 px-4 py-2.5 text-xs font-medium text-warning-600 dark:text-warning-500">
          Live updates paused: {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard icon={Users} label="Students Detected" value={stats.studentsDetected ?? 0} tone="brand" />
        <StatCard icon={Gauge} label="Average Attention" value={stats.averageAttention ?? 0} suffix="%" tone="success" />
        <StatCard icon={AlertCircle} label="Distracted Students" value={stats.distractedStudents ?? 0} tone="danger" />
        <StatCard icon={ServerCog} label="System Status" value={stats.systemStatus ?? 'Idle'} tone="success" />
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <LiveMonitoringCard students={students} frameUrl={dashboardService.getLatestFrameUrl()} />
        </div>
        <StudentPanel students={students} />
      </div>

      <DeviceStatusCard device={deviceStatus} />

      <AlertDialog />
    </div>
  );
}
