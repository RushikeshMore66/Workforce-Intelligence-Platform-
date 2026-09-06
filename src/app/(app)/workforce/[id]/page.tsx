import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getWorkerById } from '@/lib/api/workers';
import { getTeamById, getTeamLeaderById } from '@/lib/api/teams';
import { getSupervisorById } from '@/lib/api/supervisors';
import { getProjectById } from '@/lib/api/projects';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { formatDate } from '@/lib/utils';
import { ArrowLeft, Mail, Briefcase, Users } from 'lucide-react';
import { TASKS } from '@/lib/mock-data/tasks';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { getWorkerById } = await import('@/lib/api/workers');
  const w = await getWorkerById(id);
  return { title: w?.name ?? 'Worker' };
}

export default async function WorkerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const worker = await getWorkerById(id);
  if (!worker) notFound();

  const [team, supervisor] = await Promise.all([
    worker.teamId ? getTeamById(worker.teamId) : Promise.resolve(null),
    worker.supervisorId ? getSupervisorById(worker.supervisorId) : Promise.resolve(null),
  ]);

  const leader = team?.teamLeaderId ? await getTeamLeaderById(team.teamLeaderId) : null;
  const activeProject = worker.activeProjectId ? await getProjectById(worker.activeProjectId) : null;

  // Tasks assigned to this worker
  const workerTasks = TASKS.filter(t => t.assigneeId === id);

  const statusBadge = {
    ACTIVE:      { variant: 'success' as const, label: 'Active' },
    ON_LEAVE:    { variant: 'warning' as const, label: 'On Leave' },
    UNAVAILABLE: { variant: 'default' as const, label: 'Unavailable' },
  }[worker.status];

  return (
    <div className="max-w-[900px] mx-auto space-y-5">
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/workforce" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Workforce
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{worker.name}</span>
      </div>

      {/* Profile Card */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <Avatar initials={worker.avatarInitials} name={worker.name} size="lg" />
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-xl font-bold text-[#172033]">{worker.name}</h1>
              <Badge variant={statusBadge.variant} dot>{statusBadge.label}</Badge>
            </div>
            <div className="flex flex-wrap gap-3 text-sm text-[#667085]">
              <span className="flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" />{worker.role}</span>
              <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" />{worker.email}</span>
            </div>
            <div className="flex flex-wrap gap-4 mt-3 text-sm text-[#667085]">
              {team && (
                <Link href={`/teams/${team.id}`} className="flex items-center gap-1.5 hover:text-[#263B80] transition-colors">
                  <Users className="w-3.5 h-3.5 text-[#263B80]" />
                  <span className="font-medium text-[#172033]">{team.name}</span>
                </Link>
              )}
              {supervisor && (
                <Link href={`/supervisors/${supervisor.id}`} className="flex items-center gap-1.5 hover:text-[#263B80] transition-colors">
                  <Briefcase className="w-3.5 h-3.5 text-[#263B80]" />
                  <span className="font-medium text-[#172033]">{supervisor.name}</span>
                </Link>
              )}
              {leader && (
                <div className="flex items-center gap-1.5">
                  <span>Lead:</span>
                  <span className="font-medium text-[#172033]">{leader.name}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-5 pt-5 border-t border-[#E7E8EC] grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Completed', value: worker.completedTaskCount, color: 'text-[#027A48]' },
            { label: 'In Progress', value: worker.inProgressTaskCount, color: 'text-[#263B80]' },
            { label: 'Pending', value: worker.pendingTaskCount, color: 'text-[#667085]' },
            { label: 'Blocked', value: worker.blockedTaskCount, color: worker.blockedTaskCount > 0 ? 'text-[#B42318]' : 'text-[#172033]' },
          ].map(s => (
            <div key={s.label} className="text-center">
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-[#9CA3AF] mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Active Project */}
      {activeProject && (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-3">Active Project</div>
          <Link href={`/projects/${activeProject.id}`} className="flex items-center justify-between hover:opacity-75 transition-opacity">
            <div>
              <div className="font-semibold text-[#172033]">{activeProject.name}</div>
              <div className="text-xs text-[#667085] mt-0.5">{activeProject.client} · Due {formatDate(activeProject.deadline)}</div>
            </div>
            <div className="flex items-center gap-3">
              <Progress value={activeProject.progress} className="w-24" />
              <span className="text-sm font-medium text-[#172033]">{activeProject.progress}%</span>
            </div>
          </Link>
        </div>
      )}

      {/* Tasks */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC]">
          <h2 className="text-sm font-semibold text-[#172033]">Assigned Tasks ({workerTasks.length})</h2>
        </div>
        {workerTasks.length === 0 ? (
          <div className="py-12 text-center text-sm text-[#9CA3AF]">No tasks assigned.</div>
        ) : (
          <div className="divide-y divide-[#F3F4F6]">
            {workerTasks.map(task => {
              const statusCfg = {
                COMPLETED:   { variant: 'success' as const, label: 'Completed' },
                IN_PROGRESS: { variant: 'primary' as const, label: 'In Progress' },
                TODO:        { variant: 'default' as const, label: 'To Do' },
                BLOCKED:     { variant: 'danger'  as const, label: 'Blocked' },
              }[task.status];
              return (
                <div key={task.id} className="flex items-center gap-4 px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[#172033]">{task.title}</div>
                    <div className="text-xs text-[#9CA3AF] mt-0.5">Due {formatDate(task.dueDate)}</div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge variant="default" className="hidden sm:inline-flex text-[10px]">{task.priority}</Badge>
                    <Badge variant={statusCfg.variant}>{statusCfg.label}</Badge>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
