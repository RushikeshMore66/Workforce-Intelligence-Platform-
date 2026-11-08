'use client';

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { RefreshCw } from 'lucide-react';
import { useAuth } from '@/lib/auth/useAuth';
import { cn } from '@/lib/utils';
import { rise } from '@/lib/motion';

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

interface Props {
  today: string;
  lastUpdated: Date | null;
  isRefreshing: boolean;
  hasError: boolean;
  onRefresh: () => void;
}

function useAgo(date: Date | null): string {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), 15_000);
    return () => window.clearInterval(id);
  }, []);
  if (!date) return 'Syncing…';
  const s = Math.max(0, Math.round((now.getTime() - date.getTime()) / 1000));
  if (s < 10) return 'Updated just now';
  if (s < 60) return `Updated ${s}s ago`;
  return `Updated ${Math.floor(s / 60)}m ago`;
}

export function DashboardHeader({ today, lastUpdated, isRefreshing, hasError, onRefresh }: Props) {
  const { user } = useAuth();
  const ago = useAgo(lastUpdated);
  const first = user?.name.split(' ')[0];

  return (
    <motion.div variants={rise} className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <h1 className="text-[30px] leading-tight font-bold tracking-tight text-[#172033]">
          {getGreeting()}{first ? `, ${first}` : ''}
        </h1>
        <p className="text-sm text-[#667085] mt-1">
          {today} &middot; {user ? `Here's what's happening across ${user.company || 'your company'}.` : 'Loading your workspace…'}
        </p>
      </div>

      <div className="flex items-center gap-2">
        <div
          className={cn(
            'glass-pill rounded-full h-9 pl-3 pr-3.5 flex items-center gap-2 text-xs font-medium',
            hasError ? 'text-[#B42318]' : 'text-[#027A48]'
          )}
          role="status"
        >
          <span className="relative inline-flex w-2 h-2">
            <span className={cn('live-dot relative w-2 h-2 rounded-full', hasError ? 'bg-[#F04438]' : 'bg-[#12B76A]')} />
          </span>
          {hasError ? 'Some data unavailable' : 'Live'}
          <span className="text-[#9CA3AF] font-normal">· {ago}</span>
        </div>
        <button
          onClick={onRefresh}
          aria-label="Refresh dashboard"
          className="glass-pill rounded-full w-9 h-9 flex items-center justify-center text-[#667085] hover:text-[#172033] hover:bg-white active:scale-90 transition"
        >
          <RefreshCw className={cn('w-4 h-4', isRefreshing && 'animate-spin')} />
        </button>
      </div>
    </motion.div>
  );
}
