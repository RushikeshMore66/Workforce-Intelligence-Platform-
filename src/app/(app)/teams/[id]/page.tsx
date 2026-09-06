import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getTeamById, getTeamLeaderById } from '@/lib/api/teams';
import { getSupervisorById } from '@/lib/api/supervisors';
import { getWorkersByTeam } from '@/lib/api/workers';
import { getProjects } from '@/lib/api/projects';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ProjectHealthBadge } from '@/components/projects/ProjectHealthBadge';
import { formatDate } from '@/lib/utils';
import { ArrowLeft } from 'lucide-react';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const t = await getTeamById(id);
  return { title: t?.name ?? 'Team' };
}

export default async function TeamDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const team = await getTeamById(id);
  if (!team) notFound();

  const [leader, supervisor, workers, allProjects] = await Promise.all([
    team.teamLeaderId ? getTeamLeaderById(team.teamLeaderId) : Promise.resolve(null),
    team.supervisorId ? getSupervisorById(team.supervisorId) : Promise.resolve(null),
    getWorkersByTeam(id),
    getProjects(),
  ]);

  const teamProjects = allProjects.filter(p => (team.projectIds ?? []).includes(p.id));
  const totalCompleted = workers.reduce((a, w) => a + w.completedTaskCount, 0);
  const totalInProgress = workers.reduce((a, w) => a + w.inProgressTaskCount, 0);
  const totalBlocked = workers.reduce((a, w) => a + w.blockedTaskCount, 0);

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
              {supervisor && <span>Supervisor: <span className="font-medium text-[#172033]">{supervisor.name}</span></span>}
              {leader && <span>Team Lead: <span className="font-medium text-[#172033]">{leader.name}</span></span>}
            </div>
          </div>
        </div>
        <div className="mt-5 pt-5 border-t border-[#E7E8EC] grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Members',     value: workers.length },
            { label: 'Completed',   value: totalCompleted   },
            { label: 'In Progress', value: totalInProgress  },
            { label: 'Blocked',     value: totalBlocked, danger: totalBlocked > 0 },
          ].map(s => (
            <div key={s.label} className="text-center">
              <div className={`text-2xl font-bold ${s.danger ? 'text-[#B42318]' : 'text-[#172033]'}`}>{s.value}</div>
              <div className="text-xs text-[#9CA3AF] mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Members */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">Members ({workers.length})</h2>
          </div>
          <div className="divide-y divide-[#F3F4F6] max-h-[480px] overflow-y-auto">
            {workers.map(w => (
              <Link key={w.id} href={`/workforce/${w.id}`} className="flex items-center gap-3 px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
                <Avatar initials={w.avatarInitials} name={w.name} size="sm" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-[#172033] truncate">{w.name}</div>
                  <div className="text-xs text-[#667085] truncate">{w.role}</div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <Badge variant={w.status === 'ACTIVE' ? 'success' : w.status === 'ON_LEAVE' ? 'warning' : 'default'} dot>
                    {w.status === 'ACTIVE' ? 'Active' : w.status === 'ON_LEAVE' ? 'On Leave' : 'Unavailable'}
                  </Badge>
                  {w.blockedTaskCount > 0 && <Badge variant="danger">{w.blockedTaskCount} blocked</Badge>}
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Projects */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">Projects ({teamProjects.length})</h2>
          </div>
          <div className="divide-y divide-[#F3F4F6]">
            {teamProjects.length === 0 ? (
              <div className="p-6 text-center text-sm text-[#9CA3AF]">No projects assigned.</div>
            ) : (
              teamProjects.map(proj => (
                <div key={proj.id} className="px-5 py-4 hover:bg-[#F9FAFB] transition-colors">
                  <Link href={`/projects/${proj.id}`} className="text-sm font-medium text-[#172033] hover:text-[#263B80] transition-colors">
                    {proj.name}
                  </Link>
                  <div className="text-xs text-[#667085] mt-0.5 mb-2">{proj.client} · Due {formatDate(proj.deadline)}</div>
                  <div className="flex items-center gap-3">
                    <Progress value={proj.progress} className="flex-1" />
                    <span className="text-xs text-[#667085] w-8 text-right">{proj.progress}%</span>
                    <ProjectHealthBadge health={proj.health} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
