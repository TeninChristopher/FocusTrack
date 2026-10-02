import { useState } from 'react';
import { Video, ScanFace, ImageOff } from 'lucide-react';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { attentionTone } from '@/utils/format';

const TONE_COLOR = {
  success: '#22C55E',
  warning: '#F59E0B',
  danger: '#EF4444',
};

/**
 * Largest card on the dashboard. Structured so a real processed frame
 * from the backend can be dropped in with zero prop-shape changes:
 *
 * - If `frameUrl` loads successfully, it's shown directly -- the backend
 *   already burns bounding boxes/IDs/scores into the processed image
 *   (services/image_service.py: annotate_frame), so no duplicate overlay
 *   is drawn on top of a real frame.
 * - If no frame is available yet (current backend gap -- see
 *   dashboardService.getLatestFrameUrl's note) or it fails to load, this
 *   falls back to a simulated camera view built from live `students` data
 *   (GET /api/status), so the monitoring view still resembles a real
 *   AI computer-vision interface during development/demos.
 */
export function LiveMonitoringCard({ students = [], frameUrl }) {
  const [frameFailed, setFrameFailed] = useState(false);
  const showRealFrame = Boolean(frameUrl) && !frameFailed;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <Video className="h-4 w-4 text-brand-500" />
          <CardTitle className="text-slate-700 dark:text-slate-200">Live Monitoring</CardTitle>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-danger-500">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-danger-500 opacity-60" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-danger-500" />
          </span>
          LIVE
        </div>
      </CardHeader>

      <div className="relative m-5 mt-4 aspect-video overflow-hidden rounded-xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        {showRealFrame ? (
          <img
            src={frameUrl}
            alt="Latest processed classroom frame"
            className="h-full w-full object-cover"
            onError={() => setFrameFailed(true)}
          />
        ) : (
          <SimulatedOverlay students={students} />
        )}

        <div className="absolute left-3 top-3 flex items-center gap-1.5 rounded-md bg-black/40 px-2 py-1 font-data text-[10px] text-white/80 backdrop-blur-sm">
          {!showRealFrame && <ImageOff className="h-3 w-3" />}
          ESP32-CAM-01 &middot; {students.length} detected
        </div>
      </div>
    </Card>
  );
}

function SimulatedOverlay({ students }) {
  // Normalize each student's bbox center into 0-100% of the frame regardless
  // of the actual camera resolution, so this renders sensibly whether fed
  // mock data or real (differently-sized) backend bboxes.
  const xs = students.flatMap((s) => [s.bbox[0], s.bbox[2]]);
  const ys = students.flatMap((s) => [s.bbox[1], s.bbox[3]]);
  const minX = xs.length ? Math.min(...xs) : 0;
  const maxX = xs.length ? Math.max(...xs) : 1;
  const minY = ys.length ? Math.min(...ys) : 0;
  const maxY = ys.length ? Math.max(...ys) : 1;
  const spanX = Math.max(1, maxX - minX);
  const spanY = Math.max(1, maxY - minY);

  return (
    <>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(0,0,0,0.45)_100%)]" />
      <div className="pointer-events-none absolute inset-0 opacity-[0.06] [background-image:repeating-linear-gradient(0deg,#fff_0px,transparent_1px,transparent_2px)]" />
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-0 right-0 h-24 bg-gradient-to-b from-brand-400/0 via-brand-400/10 to-brand-400/0 animate-[scan_4s_linear_infinite]" />
      </div>

      {students.map((s) => {
        const cx = (s.bbox[0] + s.bbox[2]) / 2;
        const cy = (s.bbox[1] + s.bbox[3]) / 2;
        const leftPct = 8 + ((cx - minX) / spanX) * 84;
        const topPct = 12 + ((cy - minY) / spanY) * 70;
        const color = TONE_COLOR[attentionTone(s.attention_score)];

        return (
          <div
            key={s.id}
            className="absolute flex flex-col items-center transition-all duration-500"
            style={{ left: `${leftPct}%`, top: `${topPct}%`, transform: 'translate(-50%, -50%)' }}
          >
            <div
              className="relative flex h-11 w-11 items-center justify-center rounded-md"
              style={{ border: `1.5px solid ${color}`, boxShadow: `0 0 0 1px ${color}22` }}
            >
              <span className="absolute -left-px -top-px h-2 w-2 border-l-2 border-t-2" style={{ borderColor: color }} />
              <span className="absolute -right-px -top-px h-2 w-2 border-r-2 border-t-2" style={{ borderColor: color }} />
              <span className="absolute -bottom-px -left-px h-2 w-2 border-b-2 border-l-2" style={{ borderColor: color }} />
              <span className="absolute -bottom-px -right-px h-2 w-2 border-b-2 border-r-2" style={{ borderColor: color }} />
              <ScanFace className="h-4 w-4" style={{ color }} />
            </div>
            <div
              className="font-data mt-1 whitespace-nowrap rounded px-1.5 py-0.5 text-[10px] font-semibold leading-tight text-white"
              style={{ backgroundColor: `${color}CC` }}
            >
              {s.id} &middot; {s.attention_score}%
            </div>
          </div>
        );
      })}

      <style>{`
        @keyframes scan {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(420%); }
        }
      `}</style>
    </>
  );
}
