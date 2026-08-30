'use client';
import { useState, useEffect } from 'react';
import { getAnalyticsData } from '@/lib/api/analytics';
import { AnalyticsData } from '@/types';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, CartesianGrid, AreaChart, Area,
} from 'recharts';
import { SkeletonCard } from '@/components/ui/skeleton';

const CHART_COLORS = {
  completed:   '#12B76A',
  inProgress:  '#263B80',
  blocked:     '#F04438',
  backend:     '#263B80',
  frontend:    '#4F68CA',
  qa:          '#B08A3E',
  devops:      '#12B76A',
  uiux:        '#6941C6',
};

const tooltipStyle = {
  border: '1px solid #E7E8EC',
  borderRadius: 8,
  fontSize: 12,
  boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
};

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAnalyticsData().then(d => { setData(d); setLoading(false); });
  }, []);

  if (loading) return (
    <div className="max-w-[1400px] mx-auto space-y-5">
      <div className="grid sm:grid-cols-2 gap-5">
        {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
      </div>
    </div>
  );

  if (!data) return null;

  return (
    <div className="max-w-[1400px] mx-auto space-y-6">
      <div>
        <h1 className="wi-page-title">Analytics</h1>
        <p className="text-sm text-[#667085] mt-0.5">Performance metrics and workforce insights across all projects and teams.</p>
      </div>

      {/* Task Completion Trend */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-[#172033]">Task Completion Trend</h2>
          <p className="text-xs text-[#667085] mt-0.5">Completed vs In Progress vs Blocked — last 6 months</p>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data.taskCompletion} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="gradCompleted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.completed} stopOpacity={0.15} />
                <stop offset="95%" stopColor={CHART_COLORS.completed} stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradInProgress" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART_COLORS.inProgress} stopOpacity={0.15} />
                <stop offset="95%" stopColor={CHART_COLORS.inProgress} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="completed" name="Completed" stroke={CHART_COLORS.completed} fill="url(#gradCompleted)" strokeWidth={2} />
            <Area type="monotone" dataKey="inProgress" name="In Progress" stroke={CHART_COLORS.inProgress} fill="url(#gradInProgress)" strokeWidth={2} />
            <Area type="monotone" dataKey="blocked" name="Blocked" stroke={CHART_COLORS.blocked} fill="transparent" strokeWidth={2} strokeDasharray="4 4" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Team Workload */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-[#172033]">Team Workload</h2>
            <p className="text-xs text-[#667085] mt-0.5">Total vs Completed tasks per team</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.teamWorkload} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="team" tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="tasks" name="Total Tasks" fill="#EEF1FA" radius={[3,3,0,0]} />
              <Bar dataKey="completed" name="Completed" fill={CHART_COLORS.completed} radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Project Progress vs Target */}
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
          <div className="mb-4">
            <h2 className="text-sm font-semibold text-[#172033]">Project Progress vs Target</h2>
            <p className="text-xs text-[#667085] mt-0.5">Actual vs expected progress per project</p>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.projectProgress} layout="vertical" margin={{ top: 0, right: 20, left: 80, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: '#667085' }} axisLine={false} tickLine={false} width={80} />
              <Tooltip contentStyle={tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="target" name="Target" fill="#E5E7EB" radius={[0,3,3,0]} />
              <Bar dataKey="progress" name="Actual" fill={CHART_COLORS.inProgress} radius={[0,3,3,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Workload Trend */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
        <div className="mb-4">
          <h2 className="text-sm font-semibold text-[#172033]">Workload Trend by Team</h2>
          <p className="text-xs text-[#667085] mt-0.5">Active task load per team — last 7 weeks</p>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data.workloadTrend} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="backend"  name="Backend"  stroke={CHART_COLORS.backend}   strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="frontend" name="Frontend" stroke={CHART_COLORS.frontend}  strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="qa"       name="QA"       stroke={CHART_COLORS.qa}        strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="devops"   name="DevOps"   stroke={CHART_COLORS.devops}    strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="uiux"     name="UI/UX"    stroke={CHART_COLORS.uiux}      strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
