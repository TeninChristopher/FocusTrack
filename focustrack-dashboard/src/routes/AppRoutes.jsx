import { createBrowserRouter } from 'react-router-dom';
import { AppLayout } from '@/components/layout/AppLayout';
import Dashboard from '@/pages/Dashboard';
import Analytics from '@/pages/Analytics';
import Logs from '@/pages/Logs';

/**
 * Single-classroom route table -- no classroom ID param, since this
 * deployment monitors exactly one classroom (one ESP32-CAM) per the
 * backend's architecture.
 *   /           -> Dashboard
 *   /analytics  -> Analytics
 *   /logs       -> Logs
 */
export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: <Dashboard /> },
      { path: '/analytics', element: <Analytics /> },
      { path: '/logs', element: <Logs /> },
    ],
  },
]);
