'use client';

import { FolderKanban, Users, CheckSquare, AlertTriangle, TrendingUp, ShieldAlert, RefreshCw } from 'lucide-react';
import { useDashboard } from './useDashboard';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { WorkforceOverview } from '@/components/dashboard/WorkforceOverview';
import { AttentionRequired } from '@/components/dashboard/AttentionRequired';
import { WorkProgress } from '@/components/dashboard/WorkProgress';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { ProjectHealthTable } from '@/components/dashboard/ProjectHealthTable';
import { SkeletonCard } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const { metrics, attention, activities, projects, retryMetrics, retryAttention, retryActivities, retryProjects } = useDashboard();

  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  });

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <DashboardHeader today={today} />
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ECFDF3] border border-[#ABEFC6]">
            <span className="inline-block w-2 h-2 rounded-full bg-[#12B76A]" />
            <span className="text-xs font-medium text-[#027A48]">All systems operational</span>
          </div>
        </div>
      </div>

      {/* Executive KPIs */}
      {metrics.isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} className="h-[104px]" />
          ))}
        </div>
      ) : metrics.error ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 text-center shadow-sm">
          <p className="text-sm text-[#F04438] mb-3">Failed to load dashboard metrics.</p>
          <button onClick={retryMetrics} className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-[#263B80] bg-[#F3F4F6] hover:bg-[#E5E7EB] rounded-md transition-colors">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      ) : metrics.data ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <MetricCard
            title="Active Projects"
            value={metrics.data.activeProjects}
            subtitle={`${metrics.data.completedProjects} completed`}
            icon={FolderKanban}
          />
          <MetricCard
            title="Total Workers"
            value={metrics.data.totalWorkers}
            subtitle={`${metrics.data.workersActive} active today`}
            icon={Users}
          />
          <MetricCard
            title="Tasks Completed"
            value={metrics.data.tasksCompleted}
            subtitle="This quarter"
            icon={CheckSquare}
            variant="success"
          />
          <MetricCard
            title="Tasks Blocked"
            value={metrics.data.tasksBlocked}
            subtitle="Need resolution"
            icon={ShieldAlert}
            variant="danger"
          />
          <MetricCard
            title="At Risk"
            value={metrics.data.projectsAtRisk}
            subtitle={`${metrics.data.projectsDelayed} delayed`}
            icon={AlertTriangle}
            variant="warning"
          />
          <MetricCard
            title="On Track"
            value={metrics.data.projectsOnTrack}
            subtitle={`of ${metrics.data.activeProjects} active`}
            icon={TrendingUp}
            variant="success"
          />
        </div>
      ) : null}

      {/* Main content grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        {/* Left: Project Health + Work Progress */}
        <div className="xl:col-span-2 space-y-5">
          {projects.isLoading ? (
             <SkeletonCard className="h-[300px]" />
          ) : projects.error ? (
             <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 text-center shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] min-h-[300px] flex flex-col items-center justify-center">
               <p className="text-sm text-[#F04438] mb-3">Failed to load project health data.</p>
               <button onClick={retryProjects} className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-[#263B80] bg-[#F3F4F6] hover:bg-[#E5E7EB] rounded-md transition-colors">
                 <RefreshCw className="w-4 h-4" /> Retry
               </button>
             </div>
          ) : projects.data ? (
             <ProjectHealthTable projects={projects.data} supervisors={[]} />
          ) : null}

          {metrics.isLoading ? (
             <SkeletonCard className="h-[200px]" />
          ) : metrics.error ? (
             null // Handled globally above
          ) : metrics.data ? (
            <WorkProgress
              completed={metrics.data.tasksCompleted}
              inProgress={metrics.data.tasksInProgress}
              pending={metrics.data.tasksPending}
              blocked={metrics.data.tasksBlocked}
            />
          ) : null}
        </div>

        {/* Right: Attention + Workforce */}
        <div className="space-y-5">
          {attention.isLoading ? (
             <SkeletonCard className="h-[300px]" />
          ) : attention.error ? (
            <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 text-center shadow-sm flex-1 flex flex-col justify-center items-center h-[300px]">
              <p className="text-sm text-[#F04438] mb-3">Failed to load attention items.</p>
              <button onClick={retryAttention} className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-[#263B80] bg-[#F3F4F6] hover:bg-[#E5E7EB] rounded-md transition-colors">
                <RefreshCw className="w-4 h-4" /> Retry
              </button>
            </div>
          ) : attention.data ? (
            <AttentionRequired items={attention.data} />
          ) : null}

          {metrics.isLoading ? (
             <SkeletonCard className="h-[200px]" />
          ) : metrics.error ? (
             null
          ) : metrics.data ? (
            <WorkforceOverview
              totalWorkers={metrics.data.totalWorkers}
              activeToday={metrics.data.workersActive}
              onLeave={metrics.data.workersOnLeave}
              unavailable={metrics.data.workersUnavailable}
            />
          ) : null}
        </div>
      </div>

      {/* Recent Activity */}
      {activities.isLoading ? (
         <SkeletonCard className="h-[400px]" />
      ) : activities.error ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 text-center shadow-sm">
          <p className="text-sm text-[#F04438] mb-3">Failed to load recent activities.</p>
          <button onClick={retryActivities} className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-[#263B80] bg-[#F3F4F6] hover:bg-[#E5E7EB] rounded-md transition-colors">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      ) : activities.data ? (
        <RecentActivity activities={activities.data} />
      ) : null}
    </div>
  );
}