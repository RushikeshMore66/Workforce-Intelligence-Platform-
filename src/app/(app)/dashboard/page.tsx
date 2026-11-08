'use client';

import { motion } from 'motion/react';
import { FolderKanban, Users, CheckSquare, AlertTriangle, TrendingUp, ShieldAlert } from 'lucide-react';
import { useDashboard } from './useDashboard';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { HeroInsight } from '@/components/dashboard/HeroInsight';
import { ProjectTimeline } from '@/components/dashboard/ProjectTimeline';
import { WorkforceOverview } from '@/components/dashboard/WorkforceOverview';
import { AttentionRequired } from '@/components/dashboard/AttentionRequired';
import { WorkProgress } from '@/components/dashboard/WorkProgress';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { ProjectHealthTable } from '@/components/dashboard/ProjectHealthTable';
import { SectionError } from '@/components/dashboard/SectionError';
import { Skeleton } from '@/components/ui/skeleton';
import { stagger } from '@/lib/motion';

function PanelSkeleton({ className }: { className?: string }) {
  return (
    <div className={`glass rounded-[24px] p-6 space-y-4 ${className ?? ''}`} aria-busy="true">
      <Skeleton className="h-4 w-32 shimmer !animate-none" />
      <Skeleton className="h-3 w-48 shimmer" />
      <Skeleton className="h-24 w-full shimmer" />
    </div>
  );
}

export default function DashboardPage() {
  const d = useDashboard();
  const { metrics, attention, activities, projects, supervisors, teams } = d;

  const today = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const hasError = !!(metrics.error || attention.error || activities.error || projects.error);

  return (
    <motion.div variants={stagger(0.07)} initial="hidden" animate="show" className="max-w-[1400px] mx-auto space-y-5 pt-2">
      <DashboardHeader today={today} lastUpdated={d.lastUpdated} isRefreshing={d.isRefreshing} hasError={hasError} onRefresh={d.retryAll} />

      {/* Executive KPIs */}
      {metrics.isLoading ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          {Array.from({ length: 6 }).map((_, i) => <PanelSkeleton key={i} className="h-[132px] !p-5" />)}
        </div>
      ) : metrics.error ? (
        <SectionError message="Failed to load dashboard metrics." onRetry={d.retryMetrics} />
      ) : metrics.data ? (
        <motion.div variants={stagger(0.06)} className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <MetricCard title="Active Projects" value={metrics.data.activeProjects} subtitle={`${metrics.data.completedProjects} completed`} icon={FolderKanban} />
          <MetricCard title="Total Workers" value={metrics.data.totalWorkers} subtitle={`${metrics.data.workersActive} active today`} icon={Users} />
          <MetricCard title="Tasks Completed" value={metrics.data.tasksCompleted} subtitle="This quarter" icon={CheckSquare} variant="success" />
          <MetricCard title="Tasks Blocked" value={metrics.data.tasksBlocked} subtitle="Need resolution" icon={ShieldAlert} variant="danger" />
          <MetricCard title="At Risk" value={metrics.data.projectsAtRisk} subtitle={`${metrics.data.projectsDelayed} delayed`} icon={AlertTriangle} variant="warning" />
          <MetricCard title="On Track" value={metrics.data.projectsOnTrack} subtitle={`of ${metrics.data.activeProjects} active`} icon={TrendingUp} variant="success" />
        </motion.div>
      ) : null}

      {/* Timeline + hero focus card */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2">
          {projects.isLoading ? <PanelSkeleton className="h-[360px]" />
            : projects.error ? <SectionError message="Failed to load project timeline." onRetry={d.retryProjects} className="h-full" />
            : projects.data ? <ProjectTimeline projects={projects.data} supervisors={supervisors.data ?? []} /> : null}
        </div>
        {metrics.isLoading || attention.isLoading ? <PanelSkeleton className="h-[360px]" />
          : (
            <HeroInsight
              attentionCount={attention.data?.length ?? 0}
              blocked={metrics.data?.tasksBlocked ?? 0}
              atRisk={metrics.data?.projectsAtRisk ?? 0}
            />
          )}
      </div>

      {/* Details */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="xl:col-span-2 space-y-5">
          {projects.isLoading ? <PanelSkeleton className="h-[300px]" />
            : projects.error ? <SectionError message="Failed to load project health data." onRetry={d.retryProjects} />
            : projects.data ? <ProjectHealthTable projects={projects.data} supervisors={supervisors.data ?? []} /> : null}

          {metrics.isLoading ? <PanelSkeleton className="h-[240px]" />
            : metrics.data ? (
              <WorkProgress completed={metrics.data.tasksCompleted} inProgress={metrics.data.tasksInProgress} pending={metrics.data.tasksPending} blocked={metrics.data.tasksBlocked} />
            ) : null}
        </div>

        <div className="space-y-5">
          {attention.isLoading ? <PanelSkeleton className="h-[300px]" />
            : attention.error ? <SectionError message="Failed to load attention items." onRetry={d.retryAttention} />
            : attention.data ? <AttentionRequired items={attention.data} /> : null}

          {metrics.isLoading ? <PanelSkeleton className="h-[320px]" />
            : metrics.data ? (
              <WorkforceOverview
                totalWorkers={metrics.data.totalWorkers}
                activeToday={metrics.data.workersActive}
                onLeave={metrics.data.workersOnLeave}
                unavailable={metrics.data.workersUnavailable}
                teams={teams.data ?? []}
              />
            ) : null}
        </div>
      </div>

      {activities.isLoading ? <PanelSkeleton className="h-[360px]" />
        : activities.error ? <SectionError message="Failed to load recent activities." onRetry={d.retryActivities} />
        : activities.data ? <RecentActivity activities={activities.data} /> : null}
    </motion.div>
  );
}
