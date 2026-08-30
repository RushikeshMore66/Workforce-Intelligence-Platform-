import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getSupervisorById } from '@/lib/api/supervisors';
import { getProjects } from '@/lib/api/projects';
import { getWorkers } from '@/lib/api/workers';
import { getTeams } from '@/lib/api/teams';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ProjectHealthBadge } from '@/components/projects/ProjectHealthBadge';
import { daysUntil } from '@/lib/utils';
import { ArrowLeft, Mail, Users, FolderKanban } from 'lucide-react';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const s = await getSupervisorById(id);
  return { title: s?.name ?? 'Supervisor' };
}

export default async function SupervisorDetailPage({
  params,
}: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const [supervisor, allProjects, allWorkers, allTeams] = await Promise.all([
    getSupervisorById(id), getProjects(), getWorkers(), getTeams(),
  ]);

  if (!supervisor) notFound();

  const supProjects = allProjects.filter(p => supervisor.projectIds.includes(p.id));
  const supWorkers = allWorkers.filter(w => w.supervisorId === id);
  const supTeams = allTeams.filter(t => t.supervisorId === id);
  const openBlockers = supWorkers.reduce((acc, w) => acc + w.blockedTaskCount, 0);

  return (
    <div className="max-w-[1100px] mx-auto space-y-5">
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/supervisors" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Supervisors
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{supervisor.name}</span>
      </div>

      {/* Profile */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <Avatar initials={supervisor.avatarInitials} name={supervisor.name} size="lg" />
          <div className="flex-1">
            <h1 className="text-xl font-bold text-[#172033]">{supervisor.name}</h1>
            <div className="flex items-center gap-2 mt-1 text-sm text-[#667085]">
              <Mail className="w-3.5 h-3.5" />
              {supervisor.email}
            </div>
            <div className="flex flex-wrap gap-3 mt-4">
              {[
                { icon: FolderKanban, label: `${supProjects.filter(p=>p.status==='ACTIVE').length} Active Projects` },
                { icon: Users,        label: `${supWorkers.length} Workers` },
                { icon: Users,        label: `${supTeams.length} Teams` },
              ].map(item => (
                <div key={item.label} className="flex items-center gap-1.5 text-sm text-[#667085]">
                  <item.icon className="w-3.5 h-3.5 text-[#263B80]" />
                  {item.label}
                </div>
              ))}
            </div>
          </div>
          {openBlockers > 0 && (
            <Badge variant="danger">{openBlockers} blocked tasks</Badge>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Projects */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-[#E7E8EC]">
            <h2 className="text-sm font-semibold text-[#172033]">Assigned Projects</h2>
          </div>
          <div className="divide-y divide-[#F3F4F6]">
            {supProjects.length === 0 ? (
              <div className="p-6 text-center text-sm text-[#9CA3AF]">No projects assigned.</div>
            ) : (
              supProjects.map(proj => {
                const days = daysUntil(proj.deadline);
                return (
                  <div key={proj.id} className="px-5 py-4 hover:bg-[#F9FAFB] transition-colors">
                    <div className="flex items-center justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <Link href={`/projects/${proj.id}`} className="text-sm font-medium text-[#172033] hover:text-[#263B80] transition-colors block truncate">
                          {proj.name}
                        </Link>
                        <div className="text-xs text-[#667085] mt-0.5">{proj.client}</div>
                        <div className="flex items-center gap-2 mt-2">
                          <Progress value={proj.progress} className="w-24" />
                          <span className="text-xs text-[#667085]">{proj.progress}%</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1.5">
                        <ProjectHealthBadge health={proj.health} />
                        <div className={`text-xs ${days < 30 ? 'text-[#B54708]' : 'text-[#9CA3AF]'}`}>
                          {days > 0 ? `${days}d left` : 'Overdue'}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Teams & Workers */}
        <div className="space-y-5">
          <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E7E8EC]">
              <h2 className="text-sm font-semibold text-[#172033]">Teams</h2>
            </div>
            <div className="p-5 space-y-3">
              {supTeams.map(t => (
                <Link key={t.id} href={`/teams/${t.id}`} className="flex items-center justify-between p-3 border border-[#E7E8EC] rounded-lg hover:border-[#263B80]/30 hover:bg-[#EEF1FA]/30 transition-colors">
                  <div>
                    <div className="text-sm font-medium text-[#172033]">{t.name}</div>
                    <div className="text-xs text-[#667085] mt-0.5">{t.memberCount} members</div>
                  </div>
                  <Badge variant="primary">{t.memberCount}</Badge>
                </Link>
              ))}
            </div>
          </div>

          <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
            <div className="px-5 py-4 border-b border-[#E7E8EC]">
              <h2 className="text-sm font-semibold text-[#172033]">Workers ({supWorkers.length})</h2>
            </div>
            <div className="p-4 grid grid-cols-1 gap-2 max-h-72 overflow-y-auto">
              {supWorkers.slice(0, 12).map(w => (
                <Link key={w.id} href={`/workforce/${w.id}`} className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-[#F3F4F6] transition-colors">
                  <Avatar initials={w.avatarInitials} size="xs" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[#172033] truncate">{w.name}</div>
                    <div className="text-xs text-[#667085] truncate">{w.role}</div>
                  </div>
                  {w.blockedTaskCount > 0 && (
                    <Badge variant="danger">{w.blockedTaskCount}</Badge>
                  )}
                </Link>
              ))}
              {supWorkers.length > 12 && (
                <div className="text-xs text-center text-[#9CA3AF] pt-2">+{supWorkers.length - 12} more workers</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
