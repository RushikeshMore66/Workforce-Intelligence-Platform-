'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const teamData = [
  { team: 'Backend', members: 18 },
  { team: 'Frontend', members: 15 },
  { team: 'QA', members: 12 },
  { team: 'Product', members: 10 },
  { team: 'UI/UX', members: 8 },
  { team: 'DevOps', members: 7 },
];

const COLORS = ['#263B80', '#3B52A5', '#4F68CA', '#B08A3E', '#C9A85C', '#E2C87A'];

interface Props {
  totalWorkers: number;
  activeToday: number;
  onLeave: number;
  unavailable: number;
}

export function WorkforceOverview({ totalWorkers, activeToday, onLeave, unavailable }: Props) {
  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <div className="px-5 py-4 border-b border-[#E7E8EC]">
        <h2 className="text-sm font-semibold text-[#172033]">Workforce Overview</h2>
      </div>
      <div className="p-5 space-y-5">
        {/* Status grid */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Active Today', value: activeToday, color: 'text-[#027A48]' },
            { label: 'On Leave',     value: onLeave,     color: 'text-[#B54708]' },
            { label: 'Unavailable',  value: unavailable, color: 'text-[#667085]' },
          ].map(stat => (
            <div key={stat.label} className="text-center">
              <div className={`text-xl font-bold ${stat.color}`}>{stat.value}</div>
              <div className="text-[11px] text-[#9CA3AF] mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="border-t border-[#F3F4F6]" />

        {/* Team distribution chart */}
        <div>
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-3">Team Distribution</div>
          <ResponsiveContainer width="100%" height={130}>
            <BarChart data={teamData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <XAxis dataKey="team" tick={{ fontSize: 10, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ border: '1px solid #E7E8EC', borderRadius: 8, fontSize: 12 }}
                cursor={{ fill: '#F3F4F6' }}
              />
              <Bar dataKey="members" radius={[3, 3, 0, 0]}>
                {teamData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="text-xs text-[#667085] text-center">
          {totalWorkers} total workers across 6 teams
        </div>
      </div>
    </div>
  );
}
