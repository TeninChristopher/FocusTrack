import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { DateFilter } from '@/components/common/DateFilter';
import { LogsTimeline } from '@/components/logs/LogsTimeline';
import { RecordingCard } from '@/components/logs/RecordingCard';
import { VideoPlayer } from '@/components/logs/VideoPlayer';
import { CardSkeleton, LoadingSkeleton } from '@/components/common/LoadingSkeleton';
import { EmptyState } from '@/components/common/EmptyState';
import { ErrorState } from '@/components/common/ErrorState';
import { useLogs } from '@/hooks/useLogs';
import { logsService } from '@/services/logsService';

export default function Logs() {
  const {
    date,
    setDate,
    logs,
    logsLoading,
    logsError,
    refreshLogs,
    sessions,
    sessionsLoading,
    sessionsError,
  } = useLogs();

  const [selectedSessionId, setSelectedSessionId] = useState(null);

  return (
    <div className="space-y-5 pb-16">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Logs</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Event history for Classroom A-101</p>
        </div>
        <DateFilter date={date} onChange={setDate} onRefresh={refreshLogs} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Attention Event Logs</CardTitle>
        </CardHeader>
        <CardContent className="max-h-[420px] overflow-y-auto scrollbar-thin">
          {logsLoading ? (
            <LogsSkeleton />
          ) : logsError ? (
            <ErrorState message={logsError} onRetry={refreshLogs} />
          ) : (
            <LogsTimeline logs={logs || []} />
          )}
        </CardContent>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Historical Sessions</CardTitle>
          </CardHeader>
          <CardContent className="max-h-[420px] space-y-2 overflow-y-auto scrollbar-thin">
            {sessionsLoading ? (
              <div className="space-y-2">
                <CardSkeleton className="h-20" />
                <CardSkeleton className="h-20" />
              </div>
            ) : sessionsError ? (
              <ErrorState message={sessionsError} />
            ) : !sessions?.length ? (
              <EmptyState title="No sessions recorded yet" description="Sessions appear once the ESP32-CAM starts streaming." />
            ) : (
              sessions.map((session) => (
                <RecordingCard
                  key={session.id}
                  {...session}
                  active={session.id === selectedSessionId}
                  onSelect={setSelectedSessionId}
                />
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Session Playback</CardTitle>
          </CardHeader>
          <CardContent>
            <VideoPlayer
              src={selectedSessionId ? logsService.getVideoUrl(selectedSessionId) : null}
              sessionLabel={selectedSessionId}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function LogsSkeleton() {
  return (
    <div className="space-y-4 pl-6">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <LoadingSkeleton className="h-3 w-24" />
          <LoadingSkeleton className="h-4 w-full max-w-xs" />
        </div>
      ))}
    </div>
  );
}
