'use client';

import { use } from 'react';
import Link from 'next/link';
import { useTeamDetail } from './useTeamDetail';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, RefreshCw, FolderKanban } from 'lucide-react';
import { AccessDenied } from '@/components/auth/AccessDenied';
import { SkeletonCard } from '@/components/ui/skeleton';

export default function TeamDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { team, workers, isLoading, error, statusCode, refetch } = useTeamDetail(id);

  if (isLoading) {
    return (
      <div className="max-w-[1100px] mx-auto space-y-5">
        <SkeletonCard className="h-[200px]" />
        <div className="grid lg:grid-cols-2 gap-5">
          <SkeletonCard className="h-[400px]" />
          <SkeletonCard className="h-[400px]" />
        </div>
      </div>
    );
  }

  if (statusCode === 403) {
    return <AccessDenied />;
  }

  if (statusCode === 404 || !team) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] bg-white border border-[#E7E8EC] rounded-xl shadow-sm max-w-2xl mx-auto mt-10">
        <div className="text-[#9CA3AF] mb-4">
          <ArrowLeft className="w-12 h-12" />
        </div>
        <h1 className="text-xl font-bold text-[#172033] mb-2">Team Not Found</h1>
        <p className="text-sm text-[#667085] mb-6">The team you are looking for does not exist or has been removed.</p>
        <Link href="/teams" className="inline-flex items-center gap-2 px-4 py-2 bg-[#263B80] hover:bg-[#1E2E66] text-white text-sm font-medium rounded-lg transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Teams
        </Link>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-8 text-center shadow-sm max-w-lg mx-auto mt-10">
        <p className="text-sm text-[#F04438] mb-4">Failed to load team details.</p>
        <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#263B80] hover:bg-[#1E2E66] rounded-lg transition-colors">
          <RefreshCw className="w-4 h-4" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-[1100px] mx-auto space-y-5">
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/teams" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Teams
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{team.name}</span>
      </div>

      {/* Header */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <div className="w-12 h-12 rounded-xl bg-[#EEF1FA] border border-[#c7d0f0] flex items-center justify-center flex-shrink-0">
            <span className="text-lg font-bold text-[#263B80]">{team.name[0]}</span>
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-[#172033]">{team.name}</h1>
            <div className="flex flex-wrap gap-4 mt-2 text-sm text-[#667085]">
              <span>Supervisor: <span className="font-medium text-[#172033]">—</span></span>
              <span>Team Lead: <span className="font-medium text-[#172033]">—</span></span>
            </div>
          </div>
        </div>
        <div className="mt-5 pt-5 border-t border-[#E7E8EC] grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-[#172033]">{team.memberCount}</div>
            <div className="text-xs text-[#9CA3AF] mt-0.5">Members</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-[#172033]">{team.projectIds?.length || 0}</div>
            <div className="text-xs text-[#9CA3AF] mt-0.5">Projects</div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Members */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">Members ({workers.length})</h2>
          </div>
          <div className="divide-y divide-[#F3F4F6] max-h-[480px] overflow-y-auto">
            {workers.length === 0 ? (
              <div className="p-8 text-center">
                <p className="text-sm text-[#667085]">No workers found in this team.</p>
              </div>
            ) : (
              workers.map(w => (
                <div key={w.id} className="flex items-center gap-3 px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
                  <Avatar initials={w.avatarInitials} name={w.name} size="sm" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[#172033] truncate">{w.name}</div>
                    <div className="text-xs text-[#667085] truncate">{w.role}</div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge variant={w.status === 'ACTIVE' ? 'success' : w.status === 'ON_LEAVE' ? 'warning' : 'default'} dot>
                      {w.status === 'ACTIVE' ? 'Active' : w.status === 'ON_LEAVE' ? 'On Leave' : 'Unavailable'}
                    </Badge>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Projects */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">Projects</h2>
          </div>
          <div className="p-8 text-center flex flex-col items-center justify-center">
            <FolderKanban className="w-10 h-10 text-[#9CA3AF] mb-3" />
            <div className="text-[#172033] font-medium mb-1">
              {team.projectIds?.length || 0} Project{(team.projectIds?.length || 0) === 1 ? '' : 's'} Assigned
            </div>
            <p className="text-sm text-[#667085] max-w-[250px]">
              Project details are available in the dedicated Projects module.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
