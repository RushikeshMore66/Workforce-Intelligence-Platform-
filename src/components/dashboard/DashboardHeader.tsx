'use client';

import { useAuth } from '@/lib/auth/useAuth';

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export function DashboardHeader({ today }: { today: string }) {
  const { user } = useAuth();

  if (!user) {
    return (
      <div>
        <h1 className="text-2xl font-bold text-[#172033]">{getGreeting()} 👋</h1>
        <p className="text-sm text-[#667085] mt-0.5">{today} &middot; Loading your workspace...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-[#172033]">
        {getGreeting()}, {user.name.split(' ')[0]} 👋
      </h1>
      <p className="text-sm text-[#667085] mt-0.5">
        {today} &middot; Here&apos;s what&apos;s happening across {user.company || 'your company'}.
      </p>
    </div>
  );
}
