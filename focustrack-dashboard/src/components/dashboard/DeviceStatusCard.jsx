import { Camera, Server, HardDrive, Clock, Activity } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { StatusBadge } from '@/components/common/StatusBadge';
import { formatRelativeTime } from '@/utils/format';

/**
 * Reads GET /api/device-status exactly as returned by
 * services/analytics_service.get_device_status + routes/analytics_routes.py's
 * `activeTracks` addition: { esp32cam, backend, firebase, lastUpload, activeTracks }.
 *
 * This deployment has no cloud/Firebase (JSON-file storage only, per the
 * backend's local-first design), so the `firebase` field is displayed here
 * as "Storage" -- it's still the same backend key, just relabeled to match
 * what it actually represents in this architecture.
 */
export function DeviceStatusCard({ device }) {
  if (!device) return null;

  const rows = [
    { label: 'ESP32-CAM', icon: Camera, status: device.esp32cam },
    { label: 'Backend', icon: Server, status: device.backend },
    { label: 'Storage', icon: HardDrive, status: device.firebase },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Device Status</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {rows.map(({ label, icon: Icon, status }) => (
          <div key={label} className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2.5">
              <Icon className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{label}</span>
            </div>
            <StatusBadge status={status} pulse={label === 'ESP32-CAM' && status === 'Online'} />
          </div>
        ))}

        {device.activeTracks !== undefined && (
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2.5">
              <Activity className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-600 dark:text-slate-300">Active Tracking</span>
            </div>
            <span className="font-data text-xs font-semibold text-brand-600 dark:text-brand-400">
              {device.activeTracks} student{device.activeTracks === 1 ? '' : 's'}
            </span>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-slate-100 pt-3 dark:border-slate-800">
          <div className="flex items-center gap-2.5">
            <Clock className="h-4 w-4 text-slate-400" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-300">Last Upload</span>
          </div>
          <span className="font-data text-xs text-slate-400">{formatRelativeTime(device.lastUpload)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
