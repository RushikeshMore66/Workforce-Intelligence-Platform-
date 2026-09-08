'use client';

import Link from 'next/link';
import { useTeams } from './useTeams';
import { TeamViewModel } from '@/types';
import { Users, RefreshCw } from 'lucide-react';
import { SkeletonCard } from '@/components/ui/skeleton';

function TeamCard({ team }: { team: TeamViewModel }) {
  return (
    <Link href={`/teams/${team.id}`} className="block h-full">
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm hover:border-[#263B80]/30 hover:shadow-md transition-all h-full flex flex-col justify-between">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-[#172033]">{team.name}</div>
            <div className="flex items-center gap-1.5 mt-1.5">
              <span className="text-xs text-[#667085]">Lead: —</span>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-[#F3F4F6] mt-auto">
          <div className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-1.5 font-bold text-[#172033]">
              <Users className="w-3.5 h-3.5 text-[#263B80]" />
              {team.memberCount}
              <span className="text-[10px] text-[#9CA3AF] ml-1 font-normal">Members</span>
            </div>
            {team.projectIds && team.projectIds.length > 0 && (
              <div className="text-xs font-medium text-[#667085]">
                {team.projectIds.length} Project{team.projectIds.length === 1 ? '' : 's'}
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}

export default function TeamsPage() {
  const { teams, isLoading, error, refetch } = useTeams();

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      <div>
        <h1 className="wi-page-title">Teams</h1>
        <p className="text-sm text-[#667085] mt-0.5">View team composition, workload, and project assignments.</p>
      </div>

      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} className="h-[140px]" />
          ))}
        </div>
      ) : error ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-8 text-center shadow-sm max-w-lg mx-auto mt-10">
          <p className="text-sm text-[#F04438] mb-4">Failed to load teams.</p>
          <button onClick={refetch} className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-[#263B80] hover:bg-[#1E2E66] rounded-lg transition-colors">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      ) : teams.length === 0 ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm max-w-lg mx-auto mt-10">
          <Users className="w-10 h-10 text-[#9CA3AF] mx-auto mb-3" />
          <p className="text-[#172033] font-medium mb-1">No Teams Found</p>
          <p className="text-sm text-[#667085]">You do not have access to any teams.</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {teams.map(t => (
            <TeamCard key={t.id} team={t} />
          ))}
        </div>
      )}
    </div>
  );
}
