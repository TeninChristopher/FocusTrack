import { Users } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { StudentCard } from './StudentCard';
import { EmptyState } from '@/components/common/EmptyState';

/**
 * Scrollable panel of live students. Purely presentational -- re-renders
 * automatically whenever the `students` prop changes, which useDashboard's
 * polling already drives (no internal fetching/timers here).
 */
export function StudentPanel({ students = [] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Live Student Panel</CardTitle>
      </CardHeader>
      <CardContent className="max-h-[420px] space-y-0.5 overflow-y-auto scrollbar-thin pt-0">
        {students.length === 0 ? (
          <EmptyState icon={Users} title="No students detected" description="Waiting for the next frame." />
        ) : (
          students.map((s) => (
            <StudentCard
              key={s.id}
              id={s.id}
              attention_score={s.attention_score}
              attention_status={s.attention_status}
              posture={s.posture}
            />
          ))
        )}
      </CardContent>
    </Card>
  );
}
