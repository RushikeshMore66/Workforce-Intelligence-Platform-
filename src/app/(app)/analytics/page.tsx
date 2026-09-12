'use client';

import { useState, useEffect } from 'react';
import { getOrganizationAnalytics } from '@/lib/api/analytics';
import { OrganizationAnalyticsResponse } from '@/types/analytics';
import { ApiRequestError } from '@/lib/api/client';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { SkeletonCard } from '@/components/ui/skeleton';
import { AlertCircle, RefreshCw } from 'lucide-react';

const CHART_COLORS = {
  todo: '#E5E7EB',
  inProgress: '#263B80',
  blocked: '#F04438',
  completed: '#12B76A',
  overdue: '#B08A3E',
  unassigned: '#667085',
};

const tooltipStyle = {
  border: '1px solid #E7E8EC',
  borderRadius: 8,
  fontSize: 12,
  boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
};

export default function AnalyticsPage() {
  const [data, setData] = useState<OrganizationAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getOrganizationAnalytics();
      setData(response);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred while loading analytics.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-[1400px] mx-auto space-y-5">
        <div className="grid sm:grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-[1400px] mx-auto">
        <div className="bg-red-50 text-red-600 p-6 rounded-xl border border-red-100 flex flex-col items-center justify-center text-center space-y-3">
          <AlertCircle className="w-8 h-8" />
          <p className="font-medium">{error}</p>
          <button 
            onClick={loadData}
            className="flex items-center gap-2 text-sm bg-white border border-red-200 px-4 py-2 rounded hover:bg-red-50 transition"
          >
            <RefreshCw className="w-4 h-4" /> Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { workforce, workload, activity, delivery, attention } = data;

  const workloadChartData = [
    { name: 'To Do', value: workload.todo, fill: CHART_COLORS.todo },
    { name: 'In Progress', value: workload.inProgress, fill: CHART_COLORS.inProgress },
    { name: 'Blocked', value: workload.blocked, fill: CHART_COLORS.blocked },
    { name: 'Completed', value: workload.completed, fill: CHART_COLORS.completed },
    { name: 'Overdue', value: workload.overdue, fill: CHART_COLORS.overdue },
    { name: 'Unassigned', value: workload.unassigned, fill: CHART_COLORS.unassigned },
  ];

  return (
    <div className="max-w-[1400px] mx-auto space-y-8 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="wi-page-title">Organization Analytics</h1>
          <p className="text-sm text-[#667085] mt-0.5">High-level insights across all teams and projects.</p>
        </div>
        <button 
          onClick={loadData}
          className="flex items-center gap-2 text-sm bg-white border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50 transition text-gray-700 font-medium shadow-sm"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {/* Executive Summary */}
      <section>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Executive Summary</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <MetricCard title="Total Workers" value={workforce.totalWorkers ?? 0} />
          <MetricCard title="Active Workers" value={workforce.activeWorkers ?? 0} />
          <MetricCard title="Active Teams" value={workforce.activeTeams ?? 0} />
          <MetricCard title="Active Projects" value={workforce.activeProjects ?? 0} />
          <MetricCard title="Completed Tasks" value={delivery.completedTasks} />
          <MetricCard title="Completion Rate" value={`${(delivery.completionRate * 100).toFixed(1)}%`} />
        </div>
      </section>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Workforce Overview */}
        <section className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
          <h2 className="text-md font-semibold text-[#172033] mb-4">Workforce Overview</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Total Workers</span> <span className="font-medium text-gray-900">{workforce.totalWorkers ?? 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Active Workers</span> <span className="font-medium text-gray-900">{workforce.activeWorkers ?? 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Workers w/ Tasks</span> <span className="font-medium text-gray-900">{workforce.workersWithTasks ?? 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Workers w/o Tasks</span> <span className="font-medium text-gray-900">{workforce.workersWithoutTasks ?? 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Total Teams</span> <span className="font-medium text-gray-900">{workforce.totalTeams ?? 0}</span>
            </div>
            <div className="flex justify-between">
              <span>Teams w/ Workers</span> <span className="font-medium text-gray-900">{workforce.activeTeams ?? 0}</span>
            </div>
          </div>
        </section>

        {/* Workload Distribution */}
        <section className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
          <h2 className="text-md font-semibold text-[#172033] mb-4">Workload Distribution</h2>
          <div className="h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={workloadChartData} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#F3F4F6" />
                <XAxis type="number" hide />
                <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#667085' }} width={80} />
                <Tooltip contentStyle={tooltipStyle} cursor={{fill: '#f9fafb'}} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Activity Overview */}
        <section className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
          <h2 className="text-md font-semibold text-[#172033] mb-4">Activity Overview</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Total Work Updates</span> <span className="font-medium text-gray-900">{activity.totalUpdates}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Updates (Last 7 Days)</span> <span className="font-medium text-gray-900">{activity.updatesLast7Days}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Updates (Last 30 Days)</span> <span className="font-medium text-gray-900">{activity.updatesLast30Days}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Worker-Authored Updates</span> <span className="font-medium text-gray-900">{activity.workerAuthoredUpdates}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Management-Authored Updates</span> <span className="font-medium text-gray-900">{activity.managementAuthoredUpdates}</span>
            </div>
            <div className="flex justify-between">
              <span>Last Update At</span> <span className="font-medium text-gray-900">{activity.lastUpdateAt ? new Date(activity.lastUpdateAt).toLocaleString() : 'Never'}</span>
            </div>
          </div>
        </section>

        {/* Delivery Overview */}
        <section className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
          <h2 className="text-md font-semibold text-[#172033] mb-4">Delivery Overview</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Completed Tasks</span> <span className="font-medium text-gray-900">{delivery.completedTasks}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Completion Rate</span> <span className="font-medium text-gray-900">{(delivery.completionRate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Average Cycle Time (Hours)</span> <span className="font-medium text-gray-900">{delivery.averageCycleTime ? delivery.averageCycleTime.toFixed(1) : 'N/A'}</span>
            </div>
            <div className="flex justify-between border-b border-gray-100 pb-2">
              <span>Tasks with Transition History</span> <span className="font-medium text-gray-900">{delivery.tasksWithValidTransitionHistory}</span>
            </div>
            <div className="flex justify-between">
              <span>Tasks missing Transition History</span> <span className="font-medium text-gray-900">{delivery.tasksMissingTransitionHistory}</span>
            </div>
          </div>
        </section>
      </div>

      {/* Attention Required */}
      <section className="bg-orange-50 border border-orange-100 rounded-xl p-6">
        <h2 className="text-md font-semibold text-orange-900 mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-orange-600" /> Action Required / Attention
        </h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
            <p className="text-xs text-gray-500 font-medium">Overdue Tasks</p>
            <p className="text-2xl font-semibold text-orange-700 mt-1">{attention.overdueTasks}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
            <p className="text-xs text-gray-500 font-medium">Blocked Tasks</p>
            <p className="text-2xl font-semibold text-orange-700 mt-1">{attention.blockedTasks}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
            <p className="text-xs text-gray-500 font-medium">Unassigned Tasks</p>
            <p className="text-2xl font-semibold text-gray-700 mt-1">{attention.unassignedTasks}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
            <p className="text-xs text-gray-500 font-medium">At Risk Projects</p>
            <p className="text-2xl font-semibold text-orange-700 mt-1">{attention.atRiskProjects}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-orange-100">
            <p className="text-xs text-gray-500 font-medium">Idle Workers (No Activity)</p>
            <p className="text-2xl font-semibold text-gray-700 mt-1">{attention.workersWithNoRecentActivity}</p>
          </div>
        </div>
      </section>

    </div>
  );
}

function MetricCard({ title, value }: { title: string, value: string | number }) {
  return (
    <div className="bg-white border border-[#E7E8EC] p-4 rounded-xl shadow-sm">
      <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider">{title}</h3>
      <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
    </div>
  );
}
