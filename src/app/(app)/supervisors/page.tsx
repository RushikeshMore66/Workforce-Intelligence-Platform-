import Link from 'next/link';
import { getSupervisors } from '@/lib/api/supervisors';
import { getProjects } from '@/lib/api/projects';
import { getWorkers } from '@/lib/api/workers';
import { getTeams } from '@/lib/api/teams';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Supervisor, Project, Worker, Team } from '@/types';

export const metadata = { title: 'Supervisors' };

function SupervisorCard({
  supervisor, projects, workers, teams,
}: {
  supervisor: Supervisor;
  projects: Project[];
  workers: Worker[];
  teams: Team[];
}) {
  const supProjects = projects.filter(p => supervisor.projectIds.includes(p.id));
  const supWorkers = workers.filter(w => w.supervisorId === supervisor.id);
  const supTeams = teams.filter(t => t.supervisorId === supervisor.id);
  const activeProjects = supProjects.filter(p => p.status === 'ACTIVE');
  const atRisk = supProjects.filter(p => p.health === 'AT_RISK' || p.health === 'DELAYED');
  const blockedWorkers = supWorkers.filter(w => w.blockedTaskCount > 0);

  const avgProgress = supProjects.length
    ? Math.round(supProjects.reduce((acc, p) => acc + p.progress, 0) / supProjects.length)
    : 0;

  return (
    <Link href={`/supervisors/${supervisor.id}`} className="block">
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] hover:border-[#263B80]/30 hover:shadow-md transition-all">
        <div className="flex items-start gap-3 mb-4">
          <Avatar initials={supervisor.avatarInitials} name={supervisor.name} size="lg" />
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-[#172033] text-sm">{supervisor.name}</div>
            <div className="text-xs text-[#667085] mt-0.5">{supervisor.email}</div>
            <div className="flex flex-wrap gap-1.5 mt-2">
              {atRisk.length > 0 && (
                <Badge variant="warning" dot>{atRisk.length} at risk</Badge>
              )}
              {blockedWorkers.length > 0 && (
                <Badge variant="danger">{blockedWorkers.length} blocked</Badge>
              )}
              {atRisk.length === 0 && (
                <Badge variant="success" dot>On track</Badge>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 pt-4 border-t border-[#F3F4F6]">
          <div className="text-center">
            <div className="text-lg font-bold text-[#172033]">{activeProjects.length}</div>
            <div className="text-[10px] text-[#9CA3AF] uppercase tracking-wider mt-0.5">Projects</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#172033]">{supWorkers.length}</div>
            <div className="text-[10px] text-[#9CA3AF] uppercase tracking-wider mt-0.5">Workers</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-[#172033]">{avgProgress}%</div>
            <div className="text-[10px] text-[#9CA3AF] uppercase tracking-wider mt-0.5">Avg Progress</div>
          </div>
        </div>

        <div className="mt-3 space-y-1">
          {supTeams.map(t => (
            <div key={t.id} className="text-xs text-[#667085] flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#263B80]" />
              {t.name} · {t.memberCount} members
            </div>
          ))}
        </div>
      </div>
    </Link>
  );
}

export default async function SupervisorsPage() {
  const [supervisors, projects, workers, teams] = await Promise.all([
    getSupervisors(), getProjects(), getWorkers(), getTeams(),
  ]);

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      <div>
        <h1 className="wi-page-title">Supervisors</h1>
        <p className="text-sm text-[#667085] mt-0.5">Monitor supervisor workload, project health, and team oversight.</p>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-3 sm:grid-cols-5 gap-4">
        {[
          { label: 'Total', value: supervisors.length },
          { label: 'Projects', value: projects.filter(p => p.status === 'ACTIVE').length },
          { label: 'At Risk', value: projects.filter(p => p.health !== 'ON_TRACK').length },
          { label: 'Teams', value: teams.length },
          { label: 'Workers', value: workers.length },
        ].map(stat => (
          <div key={stat.label} className="bg-white border border-[#E7E8EC] rounded-xl p-4 text-center shadow-sm">
            <div className="text-xl font-bold text-[#172033]">{stat.value}</div>
            <div className="text-xs text-[#9CA3AF] mt-0.5">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {supervisors.map(sup => (
          <SupervisorCard
            key={sup.id}
            supervisor={sup}
            projects={projects}
            workers={workers}
            teams={teams}
          />
        ))}
      </div>
    </div>
  );
}
