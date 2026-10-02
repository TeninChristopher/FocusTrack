import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell, Legend } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

function barColor(value) {
  if (value >= 80) return '#22C55E';
  if (value >= 55) return '#F59E0B';
  return '#EF4444';
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs shadow-md dark:border-slate-700 dark:bg-slate-900">
      <p className="font-semibold text-slate-500">{label}</p>
      <p className="font-data font-bold" style={{ color: barColor(payload[0].value) }}>
        {payload[0].value}%
      </p>
    </div>
  );
}

/** Reads periodWise[] from GET /api/analytics: [{period, attention}]. */
export function PeriodAttentionChart({ data = [] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Period-wise Attention</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-slate-100 dark:stroke-slate-800" vertical={false} />
            <XAxis dataKey="period" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#94a3b8' }} />
            <YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} width={36} />
            <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(148,163,184,0.08)' }} />
            <Legend wrapperStyle={{ fontSize: 12 }} formatter={() => 'Average Attention'} />
            <Bar dataKey="attention" name="Average Attention" radius={[6, 6, 0, 0]} animationDuration={800}>
              {data.map((entry, index) => (
                <Cell key={index} fill={barColor(entry.attention)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
