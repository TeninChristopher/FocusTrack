import { NavLink, Link } from 'react-router-dom';
import { Activity, LayoutDashboard, LineChart, ScrollText } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ThemeToggle } from './ThemeToggle';

const CLASSROOM_NAME = 'Classroom A-101';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/analytics', label: 'Analytics', icon: LineChart },
  { to: '/logs', label: 'Logs', icon: ScrollText },
];

/** Persistent top nav shown on every page. Single-classroom deployment, so
 * "Classroom A-101" is shown as a fixed label rather than a route param. */
export function Navbar() {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-[#0b1220]/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex shrink-0 items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-white">
            <Activity className="h-4.5 w-4.5" />
          </div>
          <p className="text-sm font-extrabold tracking-tight text-slate-900 dark:text-white">
            FocusTrack
            <span className="mx-1 text-slate-300 dark:text-slate-600">&bull;</span>
            <span className="font-data text-brand-600 dark:text-brand-400">{CLASSROOM_NAME}</span>
          </p>
        </Link>

        <nav className="flex items-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-slate-800/60">
          {navItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-white text-brand-600 shadow-sm dark:bg-slate-900 dark:text-brand-400'
                    : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
                )
              }
            >
              <item.icon className="h-3.5 w-3.5" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

export { CLASSROOM_NAME };
