import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getProjectById } from '@/lib/api/projects';
import { getTasksByProject } from '@/lib/api/tasks';
import { getBlockersByProject } from '@/lib/api/blockers';
import { getActivitiesByProject } from '@/lib/api/activities';
import { getSupervisorById } from '@/lib/api/supervisors';
import { getWorkers } from '@/lib/api/workers';
import { ProjectHealthBadge } from '@/components/projects/ProjectHealthBadge';
import { ProjectStatusBadge } from '@/components/projects/ProjectStatusBadge';
import { ProjectPriorityBadge } from '@/components/projects/ProjectPriorityBadge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar } from '@/components/ui/avatar';
import { formatDate, daysUntil, timeAgo } from '@/lib/utils';
import {
  Calendar, Users, CheckSquare, ShieldAlert, ArrowLeft,
  Clock, CheckCircle2, AlertTriangle, RefreshCw, UserPlus, Pencil,
  FolderOpen, GitBranch, User, Activity,
} from 'lucide-react';
import { Task, ProjectActivity, ActivityType } from '@/types';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const project = await getProjectById(id);
  return { title: project?.name ?? 'Project' };
}

// ── Task Status Badge ──
function TaskStatusBadge({ status }: { status: Task['status'] }) {
  const cfg = {
    TODO:        { variant: 'default' as const,  label: 'To Do' },
    IN_PROGRESS: { variant: 'primary' as const,  label: 'In Progress' },
    COMPLETED:   { variant: 'success' as const,  label: 'Completed' },
    BLOCKED:     { variant: 'danger'  as const,  label: 'Blocked' },
  }[status];
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
}

// ── Activity Icon — covers all 18 ActivityType values ──
const ACTIVITY_ICON_MAP: Record<ActivityType, { Icon: React.ElementType; color: string }> = {
  TASK_COMPLETED:       { Icon: CheckCircle2, color: 'text-[#12B76A] bg-[#ECFDF3]' },
  TASK_UPDATED:         { Icon: Pencil,       color: 'text-[#263B80] bg-[#EEF1FA]' },
  TASK_CREATED:         { Icon: CheckSquare,  color: 'text-[#263B80] bg-[#EEF1FA]' },
  TASK_ASSIGNED:        { Icon: User,         color: 'text-[#B08A3E] bg-[#FBF5E8]' },
  TASK_STATUS_CHANGED:  { Icon: GitBranch,    color: 'text-[#667085] bg-[#F3F4F6]' },
  BLOCKER_REPORTED:     { Icon: AlertTriangle,color: 'text-[#F04438] bg-[#FEF3F2]' },
  BLOCKER_RESOLVED:     { Icon: CheckCircle2, color: 'text-[#12B76A] bg-[#ECFDF3]' },
  PROJECT_CREATED:      { Icon: FolderOpen,   color: 'text-[#263B80] bg-[#EEF1FA]' },
  PROJECT_UPDATED:      { Icon: RefreshCw,    color: 'text-[#667085] bg-[#F3F4F6]' },
  PROJECT_STATUS_CHANGED: { Icon: Activity,   color: 'text-[#B54708] bg-[#FFFAEB]' },
  PROJECT_ASSIGNED:     { Icon: UserPlus,     color: 'text-[#B08A3E] bg-[#FBF5E8]' },
  WORK_UPDATE_ADDED:    { Icon: Pencil,       color: 'text-[#263B80] bg-[#EEF1FA]' },
  TEAM_CREATED:         { Icon: Users,        color: 'text-[#263B80] bg-[#EEF1FA]' },
  TEAM_UPDATED:         { Icon: Users,        color: 'text-[#667085] bg-[#F3F4F6]' },
  MEMBER_ADDED:         { Icon: UserPlus,     color: 'text-[#B08A3E] bg-[#FBF5E8]' },
  MEMBER_REMOVED:       { Icon: User,         color: 'text-[#F04438] bg-[#FEF3F2]' },
  USER_CREATED:         { Icon: User,         color: 'text-[#263B80] bg-[#EEF1FA]' },
  USER_UPDATED:         { Icon: User,         color: 'text-[#667085] bg-[#F3F4F6]' },
};

function ActivityIcon({ type }: { type: ProjectActivity['type'] }) {
  const cfg = ACTIVITY_ICON_MAP[type] ?? { Icon: Activity, color: 'text-[#667085] bg-[#F3F4F6]' };
  const { Icon, color } = cfg;
  return (
    <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${color}`}>
      <Icon className="w-3.5 h-3.5" />
    </div>
  );
}

export default async function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const [project, tasks, blockers, activities, allWorkers] = await Promise.all([
    getProjectById(id),
    getTasksByProject(id),
    getBlockersByProject(id),
    getActivitiesByProject(id),
    getWorkers(),
  ]);

  if (!project) notFound();

  const supervisor = project.supervisorId
    ? await getSupervisorById(project.supervisorId)
    : null;

  const workerMap = Object.fromEntries(allWorkers.map(w => [w.id, w]));

  const openBlockers = blockers.filter(b => b.status === 'OPEN');
  const completedTasks = tasks.filter(t => t.status === 'COMPLETED').length;
  const inProgressTasks = tasks.filter(t => t.status === 'IN_PROGRESS').length;
  const pendingTasks = tasks.filter(t => t.status === 'TODO').length;
  const blockedTasks = tasks.filter(t => t.status === 'BLOCKED').length;
  const daysLeft = daysUntil(project.deadline);

  // Get unique workers on this project via tasks
  const workerIds = [...new Set(tasks.map(t => t.assigneeId).filter(Boolean))] as string[];
  const projectWorkers = workerIds.map(wid => workerMap[wid]).filter(Boolean);

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/projects" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Projects
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{project.name}</span>
      </div>

      {/* Project Header */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <ProjectStatusBadge status={project.status} />
              <ProjectHealthBadge health={project.health} />
              <ProjectPriorityBadge priority={project.priority} />
            </div>
            <h1 className="text-xl font-bold text-[#172033] leading-tight">{project.name}</h1>
            <p className="text-sm text-[#667085] mt-0.5">{project.client}</p>
            {project.description && (
              <p className="text-sm text-[#667085] mt-3 max-w-2xl leading-relaxed">{project.description}</p>
            )}
          </div>
        </div>

        {/* Stats row */}
        <div className="mt-5 pt-5 border-t border-[#E7E8EC] grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <CheckSquare className="w-3.5 h-3.5" />
              Progress
            </div>
            <div className="flex items-center gap-2">
              <Progress value={project.progress} className="flex-1" />
              <span className="text-sm font-bold text-[#172033]">{project.progress}%</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <Calendar className="w-3.5 h-3.5" />
              Deadline
            </div>
            <div className="text-sm font-semibold text-[#172033]">{formatDate(project.deadline)}</div>
            <div className={`text-xs mt-0.5 ${daysLeft < 30 ? 'text-[#B54708]' : 'text-[#667085]'}`}>
              {daysLeft > 0 ? `${daysLeft} days remaining` : 'Overdue'}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <Users className="w-3.5 h-3.5" />
              Team Members
            </div>
            <div className="text-sm font-semibold text-[#172033]">{projectWorkers.length}</div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <ShieldAlert className="w-3.5 h-3.5" />
              Open Blockers
            </div>
            <div className={`text-sm font-semibold ${openBlockers.length > 0 ? 'text-[#B42318]' : 'text-[#172033]'}`}>
              {openBlockers.length}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview">
        <div className="bg-white border border-[#E7E8EC] rounded-xl overflow-hidden shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
          <TabsList className="px-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">
              Tasks
              <Badge variant="default" className="ml-1 text-[10px] px-1.5 py-0">{tasks.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="blockers">
              Blockers
              {openBlockers.length > 0 && (
                <Badge variant="danger" className="ml-1 text-[10px] px-1.5 py-0">{openBlockers.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="p-6">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Total Tasks',    value: tasks.length,     color: 'text-[#172033]' },
                { label: 'Completed',      value: completedTasks,   color: 'text-[#027A48]' },
                { label: 'In Progress',    value: inProgressTasks,  color: 'text-[#263B80]' },
                { label: 'Pending',        value: pendingTasks,     color: 'text-[#667085]' },
                { label: 'Blocked',        value: blockedTasks,     color: 'text-[#B42318]' },
                { label: 'Started',        value: formatDate(project.startDate), color: 'text-[#172033]' },
                { label: 'Supervisor',     value: supervisor?.name ?? '—',       color: 'text-[#172033]' },
                { label: 'Team Count',     value: project.teamCount ?? '—',      color: 'text-[#172033]' },
              ].map(stat => (
                <div key={stat.label} className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                  <div className="text-xs text-[#667085] mb-1">{stat.label}</div>
                  <div className={`text-lg font-bold ${stat.color}`}>{stat.value}</div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Tasks */}
          <TabsContent value="tasks">
            <div className="divide-y divide-[#F3F4F6]">
              {tasks.length === 0 ? (
                <div className="py-16 text-center text-sm text-[#9CA3AF] p-6">No tasks for this project yet.</div>
              ) : (
                tasks.map(task => {
                  const assignee = task.assigneeId ? workerMap[task.assigneeId] : null;
                  return (
                    <div key={task.id} className="flex items-center gap-4 px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-[#172033]">{task.title}</div>
                        {assignee && (
                          <div className="flex items-center gap-1.5 mt-1">
                            <Avatar initials={assignee.avatarInitials} size="xs" />
                            <span className="text-xs text-[#667085]">{assignee.name}</span>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-3 flex-shrink-0">
                        <Badge variant="default" className="hidden sm:inline-flex text-[10px]">
                          {task.priority}
                        </Badge>
                        <div className="hidden md:flex items-center gap-1 text-xs text-[#9CA3AF]">
                          <Clock className="w-3 h-3" />
                          {formatDate(task.dueDate)}
                        </div>
                        <TaskStatusBadge status={task.status} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </TabsContent>

          {/* Blockers */}
          <TabsContent value="blockers" className="p-5">
            {blockers.length === 0 ? (
              <div className="py-12 text-center">
                <div className="text-[#12B76A] font-medium text-sm">No active blockers</div>
                <div className="text-xs text-[#9CA3AF] mt-1">All tracked work is progressing without reported blockers.</div>
              </div>
            ) : (
              <div className="space-y-3">
                {blockers.map(bl => {
                  const reporter = bl.reportedById ? workerMap[bl.reportedById] : null;
                  const ageMs = new Date().getTime() - new Date(bl.createdDate).getTime();
                  const ageDays = Math.floor(ageMs / 86400000);
                  return (
                    <div key={bl.id} className={`border rounded-lg p-4 ${
                      bl.status === 'OPEN'
                        ? 'border-[#FECDCA] bg-[#FEF3F2]'
                        : 'border-[#ABEFC6] bg-[#ECFDF3]'
                    }`}>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="text-sm font-semibold text-[#172033]">{bl.title}</span>
                            <Badge variant={bl.status === 'OPEN' ? 'danger' : 'success'} dot>
                              {bl.status === 'OPEN' ? 'Open' : 'Resolved'}
                            </Badge>
                          </div>
                          <p className="text-sm text-[#667085] mt-1.5">{bl.description}</p>
                          <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-[#9CA3AF]">
                            {reporter && (
                              <span className="flex items-center gap-1">
                                <Avatar initials={reporter.avatarInitials} size="xs" />
                                {reporter.name}
                              </span>
                            )}
                            <span>Created {formatDate(bl.createdDate)}</span>
                            {bl.status === 'OPEN' && (
                              <span className={`font-medium ${ageDays >= 3 ? 'text-[#B54708]' : 'text-[#9CA3AF]'}`}>
                                {ageDays === 0 ? 'Today' : `${ageDays} days old`}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </TabsContent>

          {/* Team */}
          <TabsContent value="team" className="p-5">
            {supervisor && (
              <div className="mb-5">
                <div className="wi-section-title mb-3">Supervisor</div>
                <Link href={`/supervisors/${project.supervisorId}`} className="flex items-center gap-3 p-3 rounded-lg hover:bg-[#F3F4F6] transition-colors group w-fit">
                  <Avatar initials={supervisor.avatarInitials} name={supervisor.name} size="md" />
                  <div>
                    <div className="text-sm font-semibold text-[#172033] group-hover:text-[#263B80] transition-colors">
                      {supervisor.name}
                    </div>
                    <div className="text-xs text-[#667085]">{supervisor.email}</div>
                  </div>
                </Link>
              </div>
            )}
            <div>
              <div className="wi-section-title mb-3">Team Members ({projectWorkers.length})</div>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {projectWorkers.map(w => (
                  <Link key={w.id} href={`/workforce/${w.id}`} className="flex items-center gap-3 p-3 border border-[#E7E8EC] rounded-lg hover:border-[#263B80]/30 hover:bg-[#EEF1FA]/30 transition-colors">
                    <Avatar initials={w.avatarInitials} name={w.name} size="sm" />
                    <div className="min-w-0">
                      <div className="text-sm font-medium text-[#172033] truncate">{w.name}</div>
                      <div className="text-xs text-[#667085] truncate">{w.role}</div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Activity */}
          <TabsContent value="activity" className="p-5">
            {activities.length === 0 ? (
              <div className="py-12 text-center text-sm text-[#9CA3AF]">No recent activity.</div>
            ) : (
              <div className="space-y-4">
                {activities.map(act => (
                  <div key={act.id} className="flex items-start gap-3">
                    <ActivityIcon type={act.type} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-[#172033]">{act.description}</p>
                      <span className="text-xs text-[#9CA3AF]">{timeAgo(act.timestamp)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
