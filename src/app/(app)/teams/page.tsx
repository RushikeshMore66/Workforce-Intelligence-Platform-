import Link from 'next/link';
import { getTeams, getAllTeamLeaders } from '@/lib/api/teams';
import { getWorkers } from '@/lib/api/workers';
import { getProjects } from '@/lib/api/projects';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Team, TeamLeader, Worker, Project } from '@/types';
import { Users } from 'lucide-react';

export const metadata = { title: 'Teams' };

function TeamCard({
  team, leader, workers, projects,
}: {
  team: Team;
  leader?: TeamLeader;
  workers: Worker[];
  projects: Project[];
}) {
  const teamWorkers = workers.filter(w => w.teamId === team.id);
  const teamProjects = projects.filter(p => (team.projectIds ?? []).includes(p.id));
  const blockedCount = teamWorkers.reduce((acc, w) => acc + w.blockedTaskCount, 0);
  const inProgressCount = teamWorkers.reduce((acc, w) => acc + w.inProgressTaskCount, 0);
  const avgProgress = teamProjects.length
    ? Math.round(teamProjects.reduce((acc, p) => acc + p.progress, 0) / teamProjects.length)
    : 0;

  const sampleInitials = teamWorkers.slice(0, 5).map(w => w.avatarInitials);

  return (
    <Link href={`/teams/${team.id}`} className="block">
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm hover:border-[#263B80]/30 hover:shadow-md transition-all">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-[#172033]">{team.name}</div>
            {leader && (
              <div className="flex items-center gap-1.5 mt-1.5">
                <Avatar initials={leader.avatarInitials} size="xs" />
                <span className="text-xs text-[#667085]">{leader.name}</span>
              </div>
            )}
          </div>
          <div className="flex -space-x-1.5">
            {sampleInitials.map((init, i) => (
              <Avatar key={i} initials={init} size="xs" className="ring-2 ring-white" />
            ))}
            {teamWorkers.length > 5 && (
              <span className="inline-flex w-6 h-6 items-center justify-center rounded-full bg-[#E5E7EB] text-[10px] font-medium text-[#667085] ring-2 ring-white">
                +{teamWorkers.length - 5}
              </span>
            )}
          </div>
        </div>

        {/* Progress */}
        {avgProgress > 0 && (
          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <span className="text-xs text-[#667085]">Avg project progress</span>
              <span className="text-xs font-medium text-[#172033]">{avgProgress}%</span>
            </div>
            <Progress value={avgProgress} />
          </div>
        )}

        <div className="grid grid-cols-3 gap-3 pt-4 border-t border-[#F3F4F6]">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-sm font-bold text-[#172033]">
              <Users className="w-3.5 h-3.5 text-[#263B80]" />
              {team.memberCount}
            </div>
            <div className="text-[10px] text-[#9CA3AF] mt-0.5">Members</div>
          </div>
          <div className="text-center">
            <div className="text-sm font-bold text-[#172033]">{inProgressCount}</div>
            <div className="text-[10px] text-[#9CA3AF] mt-0.5">In Progress</div>
          </div>
          <div className="text-center">
            <div className={`text-sm font-bold ${blockedCount > 0 ? 'text-[#B42318]' : 'text-[#172033]'}`}>{blockedCount}</div>
            <div className="text-[10px] text-[#9CA3AF] mt-0.5">Blocked</div>
          </div>
        </div>

        {teamProjects.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {teamProjects.slice(0, 2).map(p => (
              <Badge key={p.id} variant="primary" className="text-[10px]">{p.name.split(' ').slice(0, 2).join(' ')}</Badge>
            ))}
            {teamProjects.length > 2 && (
              <Badge variant="default" className="text-[10px]">+{teamProjects.length - 2} more</Badge>
            )}
          </div>
        )}
      </div>
    </Link>
  );
}

export default async function TeamsPage() {
  const [teams, leaders, workers, projects] = await Promise.all([
    getTeams(), getAllTeamLeaders(), getWorkers(), getProjects(),
  ]);

  const leaderMap = Object.fromEntries(leaders.map(l => [l.teamId, l]));

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      <div>
        <h1 className="wi-page-title">Teams</h1>
        <p className="text-sm text-[#667085] mt-0.5">View team composition, workload, and project assignments.</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {teams.map(t => (
          <TeamCard
            key={t.id}
            team={t}
            leader={leaderMap[t.id]}
            workers={workers}
            projects={projects}
          />
        ))}
      </div>
    </div>
  );
}
