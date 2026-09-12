'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useProjectDetail } from './useProjectDetail';
import { ProjectHealthBadge } from '@/components/projects/ProjectHealthBadge';
import { ProjectStatusBadge } from '@/components/projects/ProjectStatusBadge';
import { ProjectPriorityBadge } from '@/components/projects/ProjectPriorityBadge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { formatDate, daysUntil, timeAgo } from '@/lib/utils';
import {
  Calendar, Users, CheckSquare, ShieldAlert, ArrowLeft,
  Clock, CheckCircle2, AlertTriangle, RefreshCw, UserPlus, Pencil,
  FolderOpen, GitBranch, User, Activity, Search
} from 'lucide-react';
import { Task, ProjectActivity, ActivityType } from '@/types';
import { AccessDenied } from '@/components/auth/AccessDenied';
import { SkeletonCard, SkeletonTable } from '@/components/ui/skeleton';
import { isApiError } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { getProjectAnalytics } from '@/lib/api/analytics';
import { ProjectAnalyticsResponse } from '@/types/analytics';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

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

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const { project, tasks, blockers, activities, fetchProject, fetchTasks, fetchBlockers, fetchActivities } = useProjectDetail(id);
  const [activeTab, setActiveTab] = useState('overview');
  
  const [analyticsData, setAnalyticsData] = useState<ProjectAnalyticsResponse | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);

  const fetchAnalytics = React.useCallback(async () => {
    setAnalyticsLoading(true);
    setAnalyticsError(null);
    try {
      const data = await getProjectAnalytics(id);
      setAnalyticsData(data);
    } catch (err) {
      if (isApiError(err)) setAnalyticsError(err.detail);
      else setAnalyticsError('Failed to load analytics');
    } finally {
      setAnalyticsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (activeTab === 'tasks') fetchTasks();
    if (activeTab === 'blockers') fetchBlockers();
    if (activeTab === 'activity') fetchActivities();
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (activeTab === 'analytics') fetchAnalytics();
  }, [activeTab, fetchTasks, fetchBlockers, fetchActivities, fetchAnalytics]);

  if (project.isLoading && !project.hasFetched) {
    return (
      <div className="max-w-[1200px] mx-auto space-y-5">
        <SkeletonCard className="h-[200px]" />
        <SkeletonCard className="h-[400px]" />
      </div>
    );
  }

  if (project.error) {
    if (isApiError(project.error)) {
      if (project.error.status === 403) return <AccessDenied />;
      if (project.error.status === 404) {
        return (
          <div className="flex-1 flex items-center justify-center min-h-[60vh]">
            <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm w-full max-w-md">
              <div className="w-12 h-12 bg-[#F9FAFB] rounded-full flex items-center justify-center mx-auto mb-3 border border-[#E7E8EC]">
                <Search className="w-6 h-6 text-[#9CA3AF]" />
              </div>
              <h3 className="text-base font-semibold text-[#172033]">Project not found</h3>
              <p className="text-sm text-[#667085] mt-1 mb-6">The project you are looking for does not exist or has been removed.</p>
              <Link href="/projects" className="inline-flex justify-center items-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[#263B80] hover:bg-[#1E2E65] transition-colors">
                Return to Projects
              </Link>
            </div>
          </div>
        );
      }
    }
    
    return (
      <div className="flex-1 flex items-center justify-center min-h-[60vh]">
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm w-full max-w-md">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h3 className="text-base font-semibold text-[#172033]">Failed to load project</h3>
          <p className="text-sm text-[#667085] mt-1 mb-4">There was a problem communicating with the server.</p>
          <Button variant="outline" onClick={fetchProject}>
            <RefreshCw className="w-4 h-4 mr-2" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  const p = project.data;
  if (!p) return null;

  const daysLeft = daysUntil(p.deadline);
  const completedTasks = tasks.data ? tasks.data.filter(t => t.status === 'COMPLETED').length : 0;
  const inProgressTasks = tasks.data ? tasks.data.filter(t => t.status === 'IN_PROGRESS').length : 0;
  const pendingTasks = tasks.data ? tasks.data.filter(t => t.status === 'TODO').length : 0;
  const blockedTasks = tasks.data ? tasks.data.filter(t => t.status === 'BLOCKED').length : 0;
  const openBlockers = blockers.data ? blockers.data.filter(b => b.status === 'OPEN').length : 0;

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/projects" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" />
          Projects
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{p.name}</span>
      </div>

      {/* Project Header */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <ProjectStatusBadge status={p.status} />
              <ProjectHealthBadge health={p.health} />
              <ProjectPriorityBadge priority={p.priority} />
            </div>
            <h1 className="text-xl font-bold text-[#172033] leading-tight">{p.name}</h1>
            <p className="text-sm text-[#667085] mt-0.5">{p.client}</p>
            {p.description && (
              <p className="text-sm text-[#667085] mt-3 max-w-2xl leading-relaxed">{p.description}</p>
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
              <Progress value={p.progress} className="flex-1" />
              <span className="text-sm font-bold text-[#172033]">{p.progress}%</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <Calendar className="w-3.5 h-3.5" />
              Deadline
            </div>
            <div className="text-sm font-semibold text-[#172033]">{formatDate(p.deadline)}</div>
            <div className={`text-xs mt-0.5 ${daysLeft < 30 ? 'text-[#B54708]' : 'text-[#667085]'}`}>
              {daysLeft > 0 ? `${daysLeft} days remaining` : 'Overdue'}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <Users className="w-3.5 h-3.5" />
              Team Size
            </div>
            <div className="text-sm font-semibold text-[#172033]">{p.teamCount}</div>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-xs text-[#667085] mb-1">
              <ShieldAlert className="w-3.5 h-3.5" />
              Open Blockers
            </div>
            <div className={`text-sm font-semibold ${openBlockers > 0 ? 'text-[#B42318]' : 'text-[#172033]'}`}>
              {blockers.hasFetched ? openBlockers : '...'}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="bg-white border border-[#E7E8EC] rounded-xl overflow-hidden shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
          <TabsList className="px-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">
              Tasks
              {tasks.data && <Badge variant="default" className="ml-1 text-[10px] px-1.5 py-0">{tasks.data.length}</Badge>}
            </TabsTrigger>
            <TabsTrigger value="blockers">
              Blockers
              {openBlockers > 0 && (
                <Badge variant="danger" className="ml-1 text-[10px] px-1.5 py-0">{openBlockers}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="team">Team</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="p-6">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Total Tasks',    value: tasks.hasFetched && tasks.data ? tasks.data.length : '—',     color: 'text-[#172033]' },
                { label: 'Completed',      value: tasks.hasFetched ? completedTasks : '—',   color: 'text-[#027A48]' },
                { label: 'In Progress',    value: tasks.hasFetched ? inProgressTasks : '—',  color: 'text-[#263B80]' },
                { label: 'Pending',        value: tasks.hasFetched ? pendingTasks : '—',     color: 'text-[#667085]' },
                { label: 'Blocked',        value: tasks.hasFetched ? blockedTasks : '—',     color: 'text-[#B42318]' },
                { label: 'Started',        value: formatDate(p.startDate), color: 'text-[#172033]' },
                { label: 'Supervisor ID',  value: p.supervisorId ?? '—',       color: 'text-[#172033]' },
                { label: 'Team Count',     value: p.teamCount ?? '—',      color: 'text-[#172033]' },
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
            {tasks.isLoading ? (
               <div className="p-5"><SkeletonTable rows={4} cols={4} /></div>
            ) : tasks.error ? (
              <div className="p-8 text-center text-sm text-[#F04438]">
                Failed to load tasks.
                <div className="mt-2"><Button variant="outline" size="sm" onClick={fetchTasks}>Retry</Button></div>
              </div>
            ) : !tasks.data || tasks.data.length === 0 ? (
              <div className="py-16 text-center text-sm text-[#9CA3AF] p-6">No tasks for this project yet.</div>
            ) : (
              <div className="divide-y divide-[#F3F4F6]">
                {tasks.data.map(task => (
                  <div key={task.id} className="flex items-center gap-4 px-5 py-3.5 hover:bg-[#F9FAFB] transition-colors">
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-[#172033]">{task.title}</div>
                      {task.assigneeId && (
                        <div className="flex items-center gap-1.5 mt-1">
                          <span className="text-xs text-[#667085]">Assignee ID: {task.assigneeId}</span>
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
                ))}
              </div>
            )}
          </TabsContent>

          {/* Blockers */}
          <TabsContent value="blockers" className="p-5">
            {blockers.isLoading ? (
               <div className="p-5"><SkeletonTable rows={2} cols={1} /></div>
            ) : blockers.error ? (
              <div className="p-8 text-center text-sm text-[#F04438]">
                Failed to load blockers.
                <div className="mt-2"><Button variant="outline" size="sm" onClick={fetchBlockers}>Retry</Button></div>
              </div>
            ) : !blockers.data || blockers.data.length === 0 ? (
              <div className="py-12 text-center">
                <div className="text-[#12B76A] font-medium text-sm">No active blockers</div>
                <div className="text-xs text-[#9CA3AF] mt-1">All tracked work is progressing without reported blockers.</div>
              </div>
            ) : (
              <div className="space-y-3">
                {blockers.data.map(bl => {
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
                            {bl.reportedById && (
                              <span className="flex items-center gap-1">
                                Reporter ID: {bl.reportedById}
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
            <div className="py-12 text-center text-sm text-[#9CA3AF]">
               Detailed Team information will be integrated in Phase 7.8 (Workforce).
            </div>
          </TabsContent>

          {/* Activity */}
          <TabsContent value="activity" className="p-5">
            {activities.isLoading ? (
               <div className="p-5"><SkeletonTable rows={4} cols={1} /></div>
            ) : activities.error ? (
              <div className="p-8 text-center text-sm text-[#F04438]">
                Failed to load activities.
                <div className="mt-2"><Button variant="outline" size="sm" onClick={fetchActivities}>Retry</Button></div>
              </div>
            ) : !activities.data || activities.data.length === 0 ? (
              <div className="py-12 text-center text-sm text-[#9CA3AF]">No recent activity.</div>
            ) : (
              <div className="space-y-4">
                {activities.data.map(act => (
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
          {/* Analytics */}
          <TabsContent value="analytics" className="p-6 space-y-6">
            {analyticsLoading ? (
              <div className="grid sm:grid-cols-2 gap-4"><SkeletonCard className="h-32" /><SkeletonCard className="h-32" /></div>
            ) : analyticsError ? (
              <div className="p-8 text-center text-sm text-[#F04438]">
                {analyticsError}
                <div className="mt-2"><Button variant="outline" size="sm" onClick={fetchAnalytics}>Retry</Button></div>
              </div>
            ) : !analyticsData ? null : (
              <div className="space-y-6">
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                    <div className="text-xs text-[#667085] mb-1">Official Workforce (Team Members)</div>
                    <div className="text-xl font-bold text-[#172033]">{analyticsData.workforce.teamWorkforceCount ?? analyticsData.workforce.totalWorkers ?? 0}</div>
                  </div>
                  <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                    <div className="text-xs text-[#667085] mb-1">Workers with Assigned Tasks</div>
                    <div className="text-xl font-bold text-[#172033]">{analyticsData.workforce.workersWithTasks ?? 0}</div>
                  </div>
                  <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                    <div className="text-xs text-[#667085] mb-1">Total Tasks</div>
                    <div className="text-xl font-bold text-[#172033]">{analyticsData.workload.totalTasks ?? analyticsData.workload.total ?? 0}</div>
                  </div>
                  <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                    <div className="text-xs text-[#667085] mb-1">Completion Rate</div>
                    <div className="text-xl font-bold text-[#172033]">{(analyticsData.delivery.completionRate * 100).toFixed(1)}%</div>
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-6">
                  {/* Workload */}
                  <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
                    <h3 className="text-sm font-semibold mb-4">Task Workload</h3>
                    <div className="h-[200px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={[
                          { name: 'To Do', value: analyticsData.workload.todo, fill: '#E5E7EB' },
                          { name: 'In Progress', value: analyticsData.workload.inProgress, fill: '#263B80' },
                          { name: 'Blocked', value: analyticsData.workload.blocked, fill: '#F04438' },
                          { name: 'Completed', value: analyticsData.workload.completed, fill: '#12B76A' },
                          { name: 'Overdue', value: analyticsData.workload.overdue, fill: '#B08A3E' },
                          { name: 'Unassigned', value: analyticsData.workload.unassigned, fill: '#667085' },
                        ]} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#F3F4F6" />
                          <XAxis type="number" hide />
                          <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#667085' }} width={80} />
                          <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12, border: '1px solid #E7E8EC' }} cursor={{fill: '#f9fafb'}} />
                          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Activity & Delivery */}
                  <div className="space-y-4">
                    <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
                      <h3 className="text-sm font-semibold mb-4">Activity Insights</h3>
                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex justify-between border-b pb-1"><span>Total Work Updates</span><span className="font-medium text-gray-900">{analyticsData.activity.totalUpdates}</span></div>
                        <div className="flex justify-between border-b pb-1"><span>Worker-Authored Updates</span><span className="font-medium text-gray-900">{analyticsData.activity.workerAuthoredUpdates}</span></div>
                        <div className="flex justify-between"><span>Management-Authored Updates</span><span className="font-medium text-gray-900">{analyticsData.activity.managementAuthoredUpdates}</span></div>
                      </div>
                    </div>
                    
                    <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
                      <h3 className="text-sm font-semibold mb-4">Delivery Insights</h3>
                      <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex justify-between border-b pb-1"><span>Completed Tasks</span><span className="font-medium text-gray-900">{analyticsData.delivery.completedTasks}</span></div>
                        <div className="flex justify-between border-b pb-1"><span>Avg Cycle Time (Hours)</span><span className="font-medium text-gray-900">{analyticsData.delivery.averageCycleTime ? analyticsData.delivery.averageCycleTime.toFixed(1) : 'N/A'}</span></div>
                        <div className="flex justify-between border-b pb-1"><span>Tasks w/ Transition History</span><span className="font-medium text-gray-900">{analyticsData.delivery.tasksWithValidTransitionHistory}</span></div>
                        <div className="flex justify-between"><span>Missing Transition History</span><span className="font-medium text-gray-900">{analyticsData.delivery.tasksMissingTransitionHistory}</span></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
