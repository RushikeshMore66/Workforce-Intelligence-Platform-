import { Suspense } from 'react';
import { FolderKanban, Users, CheckSquare, AlertTriangle, TrendingUp, ShieldAlert } from 'lucide-react';
import { getDashboardMetrics, getAttentionItems, getRecentActivities } from '@/lib/api/dashboard';
import { getProjects } from '@/lib/api/projects';
import { getSupervisors } from '@/lib/api/supervisors';
import { currentUser } from '@/lib/auth';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { ProjectHealthTable } from '@/components/dashboard/ProjectHealthTable';
import { WorkforceOverview } from '@/components/dashboard/WorkforceOverview';
import { AttentionRequired } from '@/components/dashboard/AttentionRequired';
import { WorkProgress } from '@/components/dashboard/WorkProgress';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { SkeletonCard } from '@/components/ui/skeleton';

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export const metadata = { title: 'Dashboard' };

export default async function DashboardPage() {
  const [metrics, attentionItems, activities, projects, supervisors] = await Promise.all([
    getDashboardMetrics(),
    getAttentionItems(),
    getRecentActivities(),
    getProjects(),
    getSupervisors(),
  ]);

  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-[#172033]">
            {getGreeting()}, {currentUser.name.split(' ')[0]} 👋
          </h1>
          <p className="text-sm text-[#667085] mt-0.5">
            {today} &middot; Here&apos;s what&apos;s happening across {currentUser.company}.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECFDF3] border border-[#ABEFC6]">
            <span className="inline-block w-2 h-2 rounded-full bg-[#12B76A]" />
            <span className="text-xs font-medium text-[#027A48]">All systems operational</span>
          </div>
        </div>
      </div>

      {/* Executive KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <MetricCard
          title="Active Projects"
          value={metrics.activeProjects}
          subtitle={`${metrics.completedProjects} completed`}
          icon={FolderKanban}
        />
        <MetricCard
          title="Total Workers"
          value={metrics.totalWorkers}
          subtitle={`${metrics.workersActive} active today`}
          icon={Users}
        />
        <MetricCard
          title="Tasks Completed"
          value={metrics.tasksCompleted}
          subtitle="This quarter"
          icon={CheckSquare}
          variant="success"
        />
        <MetricCard
          title="Tasks Blocked"
          value={metrics.tasksBlocked}
          subtitle="Need resolution"
          icon={ShieldAlert}
          variant="danger"
        />
        <MetricCard
          title="At Risk"
          value={metrics.projectsAtRisk}
          subtitle={`${metrics.projectsDelayed} delayed`}
          icon={AlertTriangle}
          variant="warning"
        />
        <MetricCard
          title="On Track"
          value={metrics.projectsOnTrack}
          subtitle={`of ${metrics.activeProjects} active`}
          icon={TrendingUp}
          variant="success"
        />
      </div>

      {/* Main content grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        {/* Left: Project Health + Work Progress */}
        <div className="xl:col-span-2 space-y-5">
          <Suspense fallback={<SkeletonCard />}>
            <ProjectHealthTable projects={projects} supervisors={supervisors} />
          </Suspense>
          <WorkProgress
            completed={metrics.tasksCompleted}
            inProgress={metrics.tasksInProgress}
            pending={metrics.tasksPending}
            blocked={metrics.tasksBlocked}
          />
        </div>

        {/* Right: Attention + Workforce */}
        <div className="space-y-5">
          <AttentionRequired items={attentionItems} />
          <WorkforceOverview
            totalWorkers={metrics.totalWorkers}
            activeToday={metrics.workersActive}
            onLeave={metrics.workersOnLeave}
            unavailable={metrics.workersUnavailable}
          />
        </div>
      </div>

      {/* Recent Activity */}
      <RecentActivity activities={activities} />
    </div>
  );
}