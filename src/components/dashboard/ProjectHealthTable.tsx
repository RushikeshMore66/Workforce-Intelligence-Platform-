import Link from 'next/link';
import { Project, Supervisor } from '@/types';
import { Progress } from '@/components/ui/progress';
import { ArrowRight } from 'lucide-react';

interface Props {
  projects: Project[];
  supervisors: Supervisor[];
}

function HealthDot({ health }: { health: Project['health'] }) {
  const colors = {
    ON_TRACK: 'bg-[#12B76A]',
    AT_RISK:  'bg-[#F79009]',
    DELAYED:  'bg-[#F04438]',
  };
  const labels = { ON_TRACK: 'On Track', AT_RISK: 'At Risk', DELAYED: 'Delayed' };
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`inline-block w-2 h-2 rounded-full ${colors[health]}`} />
      <span className={`text-xs font-medium ${
        health === 'ON_TRACK' ? 'text-[#027A48]' :
        health === 'AT_RISK'  ? 'text-[#B54708]' : 'text-[#B42318]'
      }`}>{labels[health]}</span>
    </span>
  );
}

export function ProjectHealthTable({ projects, supervisors }: Props) {
  const supMap = Object.fromEntries(supervisors.map(s => [s.id, s]));
  const topProjects = projects
    .filter(p => p.status === 'ACTIVE')
    .sort((a, b) => {
      const healthOrder = { DELAYED: 0, AT_RISK: 1, ON_TRACK: 2 };
      return healthOrder[a.health] - healthOrder[b.health];
    })
    .slice(0, 6);

  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <div className="flex items-center justify-between px-5 py-4 border-b border-[#E7E8EC]">
        <h2 className="text-sm font-semibold text-[#172033]">Project Health</h2>
        <Link href="/projects" className="text-xs font-medium text-[#263B80] hover:underline flex items-center gap-1">
          View all <ArrowRight className="w-3 h-3" />
        </Link>
      </div>

      <div className="divide-y divide-[#F3F4F6]">
        {topProjects.map(proj => {
          const sup = supMap[proj.supervisorId];
          const daysLeft = Math.ceil(
            (new Date(proj.deadline).getTime() - new Date().getTime()) / 86400000
          );
          return (
            <div key={proj.id} className="px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
              <div className="flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <Link href={`/projects/${proj.id}`} className="text-sm font-medium text-[#172033] hover:text-[#263B80] truncate block transition-colors">
                    {proj.name}
                  </Link>
                  <div className="text-xs text-[#667085] mt-0.5">{proj.client}</div>
                </div>
                <div className="hidden md:flex items-center gap-1 text-xs text-[#667085] min-w-[100px]">
                  {sup?.name ?? '—'}
                </div>
                <div className="flex items-center gap-2 min-w-[120px]">
                  <Progress value={proj.progress} className="flex-1" />
                  <span className="text-xs text-[#667085] font-medium w-8 text-right">{proj.progress}%</span>
                </div>
                <div className="hidden sm:block min-w-[72px] text-right">
                  <HealthDot health={proj.health} />
                </div>
                <div className={`text-xs font-medium min-w-[64px] text-right ${daysLeft < 30 ? 'text-[#B54708]' : 'text-[#667085]'}`}>
                  {daysLeft > 0 ? `${daysLeft}d` : 'Overdue'}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
