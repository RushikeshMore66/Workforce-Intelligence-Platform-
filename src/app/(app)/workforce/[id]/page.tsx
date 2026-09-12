'use client';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useWorkerDetail } from './useWorkerDetail';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Mail, Briefcase, Users, AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SkeletonTable, SkeletonCard } from '@/components/ui/skeleton';
import { useEffect, useState } from 'react';
import { getWorkerAnalytics } from '@/lib/api/analytics';
import { WorkerAnalyticsResponse } from '@/types/analytics';
import { isApiError } from '@/lib/api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function WorkerDetailPage() {
  const params = useParams();
  const id = params.id as string;
  
  const { worker, fetchWorker } = useWorkerDetail(id);
  const { data: w, isLoading, error } = worker;

  const [analyticsData, setAnalyticsData] = useState<WorkerAnalyticsResponse | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setAnalyticsLoading(true);
      setAnalyticsError(null);
      try {
        const data = await getWorkerAnalytics(id);
        setAnalyticsData(data);
      } catch (err) {
        if (isApiError(err)) setAnalyticsError(err.detail);
        else setAnalyticsError('Failed to load worker analytics.');
      } finally {
        setAnalyticsLoading(false);
      }
    };
    fetchAnalytics();
  }, [id]);

  if (isLoading) {
    return (
      <div className="max-w-[900px] mx-auto space-y-5">
        <SkeletonTable rows={4} cols={1} />
      </div>
    );
  }

  if (error) {
    const errorMsg = error.message.toLowerCase();
    const is403 = errorMsg.includes('403') || errorMsg.includes('forbidden') || errorMsg.includes('unauthorized');
    const is404 = errorMsg.includes('404') || errorMsg.includes('not found');
    const is401 = errorMsg.includes('401') || errorMsg.includes('unauthenticated');

    return (
      <div className="max-w-[900px] mx-auto space-y-5">
        <div className="flex items-center gap-2 text-sm text-[#667085]">
          <Link href="/workforce" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> Workforce
          </Link>
        </div>
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h3 className="text-base font-semibold text-[#172033]">
            {is404 ? 'Worker not found' : is403 ? 'Access denied' : is401 ? 'Authentication required' : 'Unable to load worker'}
          </h3>
          <p className="text-sm text-[#667085] mt-1 mb-4">
            {is404 ? 'The requested worker profile does not exist.' :
             is403 ? 'You do not have permission to view this worker.' :
             is401 ? 'Please log in again to continue.' :
             'There was a problem communicating with the server.'}
          </p>
          {(!is403 && !is404) && (
            <Button variant="outline" onClick={fetchWorker}>
              <RefreshCw className="w-4 h-4 mr-2" /> Retry
            </Button>
          )}
        </div>
      </div>
    );
  }

  if (!w) return null;

  const statusBadge = {
    ACTIVE:      { variant: 'success' as const, label: 'Active' },
    ON_LEAVE:    { variant: 'warning' as const, label: 'On Leave' },
    UNAVAILABLE: { variant: 'default' as const, label: 'Unavailable' },
  }[w.status];

  return (
    <div className="max-w-[900px] mx-auto space-y-5">
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/workforce" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Workforce
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{w.name}</span>
      </div>

      {/* Profile Section */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <Avatar initials={w.avatarInitials} name={w.name} size="lg" />
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-xl font-bold text-[#172033]">{w.name}</h1>
              <Badge variant={statusBadge.variant} dot>{statusBadge.label}</Badge>
            </div>
            <div className="flex flex-wrap gap-3 text-sm text-[#667085]">
              <span className="flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" />{w.role}</span>
              <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" />{w.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Organization & Active Project Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5" />
            Organization
          </div>
          <div className="space-y-4">
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Team ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.teamId ?? '—'}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Team Leader ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.teamLeaderId ?? '—'}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Supervisor ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.supervisorId ?? '—'}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm h-fit">
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Briefcase className="w-3.5 h-3.5" />
            Current Project
          </div>
          <div>
            <div className="text-xs text-[#9CA3AF] mb-1">Active Project ID</div>
            <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
              {w.activeProjectId ?? '—'}
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Section */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden p-6 mt-5">
        <h2 className="text-lg font-semibold text-[#172033] mb-5">Worker Analytics</h2>
        {analyticsLoading ? (
          <div className="grid sm:grid-cols-2 gap-4"><SkeletonCard className="h-32" /><SkeletonCard className="h-32" /></div>
        ) : analyticsError ? (
          <div className="p-8 text-center text-sm text-[#F04438]">
            {analyticsError}
          </div>
        ) : !analyticsData ? null : (
          <div className="space-y-6">
            {/* Workload */}
            <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
              <h3 className="text-sm font-semibold mb-4">Workload</h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                  <div className="text-xs text-[#667085] mb-1">Total Tasks</div>
                  <div className="text-xl font-bold text-[#172033]">{analyticsData.workload.totalTasks ?? analyticsData.workload.total ?? 0}</div>
                </div>
                <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                  <div className="text-xs text-[#667085] mb-1">Overdue</div>
                  <div className="text-xl font-bold text-[#B08A3E]">{analyticsData.workload.overdue ?? 0}</div>
                </div>
                <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                  <div className="text-xs text-[#667085] mb-1">Blocked</div>
                  <div className="text-xl font-bold text-[#F04438]">{analyticsData.workload.blocked ?? 0}</div>
                </div>
                <div className="bg-[#F9FAFB] border border-[#E7E8EC] rounded-lg p-4">
                  <div className="text-xs text-[#667085] mb-1">Completed</div>
                  <div className="text-xl font-bold text-[#12B76A]">{analyticsData.workload.completed ?? 0}</div>
                </div>
              </div>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { name: 'To Do', value: analyticsData.workload.todo, fill: '#E5E7EB' },
                    { name: 'In Progress', value: analyticsData.workload.inProgress, fill: '#263B80' },
                    { name: 'Blocked', value: analyticsData.workload.blocked, fill: '#F04438' },
                    { name: 'Completed', value: analyticsData.workload.completed, fill: '#12B76A' },
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

            <div className="grid lg:grid-cols-2 gap-6">
              {/* Activity */}
              <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold mb-4">Activity</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between border-b pb-1"><span>Total Work Updates</span><span className="font-medium text-gray-900">{analyticsData.activity.totalUpdates}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Updates (Last 7 Days)</span><span className="font-medium text-gray-900">{analyticsData.activity.updatesLast7Days}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Updates (Last 30 Days)</span><span className="font-medium text-gray-900">{analyticsData.activity.updatesLast30Days}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Worker-Authored</span><span className="font-medium text-gray-900">{analyticsData.activity.workerAuthoredUpdates}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Management-Authored</span><span className="font-medium text-gray-900">{analyticsData.activity.managementAuthoredUpdates}</span></div>
                  <div className="flex justify-between"><span>Last Update At</span><span className="font-medium text-gray-900">{analyticsData.activity.lastUpdateAt ? new Date(analyticsData.activity.lastUpdateAt).toLocaleString() : 'Never'}</span></div>
                </div>
              </div>
              
              {/* Delivery */}
              <div className="border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-semibold mb-4">Delivery</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between border-b pb-1"><span>Completed Tasks</span><span className="font-medium text-gray-900">{analyticsData.delivery.completedTasks}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Completion Rate</span><span className="font-medium text-gray-900">{(analyticsData.delivery.completionRate * 100).toFixed(1)}%</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Avg Cycle Time (Hours)</span><span className="font-medium text-gray-900">{analyticsData.delivery.averageCycleTime ? analyticsData.delivery.averageCycleTime.toFixed(1) : 'N/A'}</span></div>
                  <div className="flex justify-between border-b pb-1"><span>Tasks w/ Transition History</span><span className="font-medium text-gray-900">{analyticsData.delivery.tasksWithValidTransitionHistory}</span></div>
                  <div className="flex justify-between"><span>Missing Transition History</span><span className="font-medium text-gray-900">{analyticsData.delivery.tasksMissingTransitionHistory}</span></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
