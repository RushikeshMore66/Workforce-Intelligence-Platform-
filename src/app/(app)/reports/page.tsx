import { Download, TrendingUp, Users, FolderKanban, CheckSquare } from 'lucide-react';

export const metadata = { title: 'Reports' };

const REPORTS = [
  {
    id: 'rep-1', icon: TrendingUp, category: 'Project', title: 'Project Health Summary',
    description: 'Overview of all active projects — progress, health status, blockers, and deadlines.',
    updated: 'Aug 30, 2026', format: 'PDF',
  },
  {
    id: 'rep-2', icon: Users, category: 'Workforce', title: 'Workforce Utilization Report',
    description: 'Worker activity rates, availability, and task distribution across all teams.',
    updated: 'Aug 29, 2026', format: 'Excel',
  },
  {
    id: 'rep-3', icon: CheckSquare, category: 'Tasks', title: 'Task Completion Analysis',
    description: 'Completed vs pending tasks by team, month, and priority level.',
    updated: 'Aug 28, 2026', format: 'PDF',
  },
  {
    id: 'rep-4', icon: FolderKanban, category: 'Project', title: 'Supervisor Performance Report',
    description: 'Project delivery rates, blocker resolution times, and team health per supervisor.',
    updated: 'Aug 27, 2026', format: 'PDF',
  },
  {
    id: 'rep-5', icon: TrendingUp, category: 'Analytics', title: 'Monthly Progress Report — August 2026',
    description: 'Month-over-month comparison of project milestones, task velocity, and team workload.',
    updated: 'Aug 30, 2026', format: 'PDF',
  },
  {
    id: 'rep-6', icon: Users, category: 'Workforce', title: 'Leave & Availability Report',
    description: 'Summary of worker leave patterns, upcoming unavailability, and impact on projects.',
    updated: 'Aug 25, 2026', format: 'Excel',
  },
];

const CATEGORY_COLORS: Record<string, string> = {
  Project: 'bg-[#EEF1FA] text-[#263B80]',
  Workforce: 'bg-[#FBF5E8] text-[#B08A3E]',
  Tasks: 'bg-[#ECFDF3] text-[#027A48]',
  Analytics: 'bg-[#EFF8FF] text-[#1849A9]',
};

export default function ReportsPage() {
  return (
    <div className="max-w-[1100px] mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="wi-page-title">Reports</h1>
          <p className="text-sm text-[#667085] mt-0.5">Pre-built reports and exportable summaries for leadership review.</p>
        </div>
      </div>

      <div className="bg-[#FFFAEB] border border-[#FEDF89] rounded-xl px-5 py-3.5 text-sm text-[#B54708]">
        <strong>Demo mode:</strong> Report download functionality will be connected to the backend API. Click the download button to simulate export.
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {REPORTS.map(r => {
          const Icon = r.icon;
          return (
            <div key={r.id} className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm hover:border-[#263B80]/30 hover:shadow-md transition-all">
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg bg-[#EEF1FA] flex items-center justify-center flex-shrink-0">
                  <Icon className="w-4.5 h-4.5 text-[#263B80]" />
                </div>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${CATEGORY_COLORS[r.category]}`}>
                  {r.category}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-[#172033] leading-snug">{r.title}</h3>
              <p className="text-xs text-[#667085] mt-1.5 leading-relaxed line-clamp-2">{r.description}</p>
              <div className="mt-4 pt-4 border-t border-[#F3F4F6] flex items-center justify-between">
                <div className="text-[11px] text-[#9CA3AF]">
                  Updated {r.updated}
                </div>
                <button className="flex items-center gap-1.5 text-xs font-medium text-[#263B80] hover:underline">
                  <Download className="w-3.5 h-3.5" />
                  {r.format}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
