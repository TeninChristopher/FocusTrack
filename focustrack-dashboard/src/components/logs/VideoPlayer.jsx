import { useState } from 'react';
import { VideoOff } from 'lucide-react';

/**
 * Plays a session's video from GET /api/video/{session_id} (a direct
 * FileResponse stream from logs_routes.py -- `src` is the URL itself,
 * not a fetch() result). Uses the native HTML5 <video> element, which
 * already provides play/pause/seek/volume/fullscreen controls, so no
 * custom control UI is reinvented here.
 */
export function VideoPlayer({ src, sessionLabel }) {
  const [failed, setFailed] = useState(false);

  if (!src) {
    return (
      <div className="flex aspect-video items-center justify-center rounded-xl bg-slate-100 text-sm text-slate-400 dark:bg-slate-800/60">
        Select a session to play its recording.
      </div>
    );
  }

  if (failed) {
    return (
      <div className="flex aspect-video flex-col items-center justify-center gap-2 rounded-xl bg-slate-100 text-slate-400 dark:bg-slate-800/60">
        <VideoOff className="h-6 w-6" />
        <p className="text-sm font-medium">Couldn't load this recording.</p>
      </div>
    );
  }

  return (
    <video
      key={src}
      controls
      className="aspect-video w-full rounded-xl bg-black"
      aria-label={sessionLabel ? `Recording for ${sessionLabel}` : 'Session recording'}
      onError={() => setFailed(true)}
    >
      <source src={src} type="video/mp4" />
      Your browser does not support video playback.
    </video>
  );
}
