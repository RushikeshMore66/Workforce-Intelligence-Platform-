'use client';

import { useAuth } from '@/lib/auth/useAuth';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';

export function ProfileCard() {
  const { user } = useAuth();

  if (!user) {
    return (
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm animate-pulse">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-[#F3F4F6]" />
          <div className="space-y-2">
            <div className="h-4 bg-[#F3F4F6] rounded w-32" />
            <div className="h-3 bg-[#F3F4F6] rounded w-48" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
      <div className="flex items-center gap-4">
        <Avatar initials={user.avatarInitials} name={user.name} size="lg" />
        <div>
          <div className="font-semibold text-[#172033] text-base">{user.name}</div>
          <div className="text-sm text-[#667085]">{user.email}</div>
          <div className="mt-2">
            <Badge variant="gold" dot>{user.role}</Badge>
          </div>
        </div>
      </div>
    </div>
  );
}
