'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { TeamViewModel } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { AnimatedNumber } from '@/components/ui/animated-number';

const COLORS = ['#263B80', '#3B52A5', '#4F68CA', '#B08A3E', '#C9A85C', '#E2C87A'];

interface Props {
  totalWorkers: number;
  activeToday: number;
  onLeave: number;
  unavailable: number;
  teams: TeamViewModel[];
}

export function WorkforceOverview({ totalWorkers, activeToday, onLeave, unavailable, teams }: Props) {
  const teamData = [...teams]
    .sort((a, b) => b.memberCount - a.memberCount)
    .slice(0, 6)
    .map(t => ({ team: t.name.length > 9 ? `${t.name.slice(0, 8)}…` : t.name, full: t.name, members: t.memberCount }));

  const stats = [
    { label: 'Active', value: activeToday, tone: 'bg-[#ECFDF3] text-[#027A48]' },
    { label: 'On leave', value: onLeave, tone: 'bg-[#FFFAEB] text-[#B54708]' },
    { label: 'Unavailable', value: unavailable, tone: 'bg-[#F3F4F6] text-[#667085]' },
  ];

  return (
    <GlassPanel title="Workforce Overview" subtitle={`${totalWorkers.toLocaleString('en-IN')} total workers`} bodyClassName="p-6 pt-2 space-y-5">
      <div className="grid grid-cols-3 gap-2.5">
        {stats.map(s => (
          <div key={s.label} className={`rounded-2xl px-3 py-3 text-center ${s.tone}`}>
            <AnimatedNumber value={s.value} className="text-xl font-bold tabular-nums" />
            <div className="text-[11px] mt-0.5 opacity-80">{s.label}</div>
          </div>
        ))}
      </div>

      <div>
        <div className="text-[11px] font-semibold text-[#9CA3AF] uppercase tracking-wider mb-2">Team distribution</div>
        {teamData.length === 0 ? (
          <p className="text-xs text-[#667085] py-6 text-center">No team data available.</p>
        ) : (
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={teamData} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
              <XAxis dataKey="team" tick={{ fontSize: 10, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#9CA3AF' }} axisLine={false} tickLine={false} />
              <Tooltip
                labelFormatter={(_, p) => p?.[0]?.payload?.full ?? ''}
                contentStyle={{ border: 'none', borderRadius: 12, fontSize: 12, boxShadow: '0 10px 30px -10px rgba(23,32,51,0.3)' }}
                cursor={{ fill: 'rgba(38,59,128,0.06)', radius: 8 }}
              />
              <Bar dataKey="members" radius={[8, 8, 8, 8]} animationDuration={900}>
                {teamData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </GlassPanel>
  );
}
