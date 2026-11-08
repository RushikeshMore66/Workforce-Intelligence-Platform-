'use client';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'motion/react';
import { GlassPanel } from '@/components/ui/glass-panel';
import { AnimatedNumber } from '@/components/ui/animated-number';
import { EASE_OUT } from '@/lib/motion';

interface Props { completed: number; inProgress: number; pending: number; blocked: number }

const COLORS = ['#12B76A', '#263B80', '#C4C9D4', '#F04438'];

export function WorkProgress({ completed, inProgress, pending, blocked }: Props) {
  const data = [
    { name: 'Completed', value: completed },
    { name: 'In Progress', value: inProgress },
    { name: 'Pending', value: pending },
    { name: 'Blocked', value: blocked },
  ];
  const total = completed + inProgress + pending + blocked;
  const pct = total ? Math.round((completed / total) * 100) : 0;

  return (
    <GlassPanel title="Work Progress" subtitle={`${total.toLocaleString('en-IN')} total work items`} bodyClassName="p-6 pt-2 flex flex-col sm:flex-row items-center gap-6">
      <div className="relative w-full sm:w-48 h-44 flex-shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={total ? data : [{ name: 'None', value: 1 }]} cx="50%" cy="50%" innerRadius={56} outerRadius={78} paddingAngle={total ? 3 : 0} cornerRadius={6} dataKey="value" stroke="none" animationDuration={1100} animationEasing="ease-out">
              {(total ? data : [{ name: 'None', value: 1 }]).map((_, i) => <Cell key={i} fill={total ? COLORS[i] : '#E5E7EB'} />)}
            </Pie>
            <Tooltip contentStyle={{ border: 'none', borderRadius: 12, fontSize: 12, boxShadow: '0 10px 30px -10px rgba(23,32,51,0.3)' }} />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-[#172033] tabular-nums"><AnimatedNumber value={pct} />%</span>
          <span className="text-[10px] uppercase tracking-wider text-[#9CA3AF]">complete</span>
        </div>
      </div>

      <div className="flex-1 space-y-3 w-full">
        {data.map((d, i) => (
          <div key={d.name}>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="flex items-center gap-2 text-[#667085]"><span className="w-2 h-2 rounded-full" style={{ background: COLORS[i] }} />{d.name}</span>
              <span className="font-semibold text-[#172033] tabular-nums">{d.value.toLocaleString('en-IN')}</span>
            </div>
            <div className="h-1.5 rounded-full bg-[#E5E7EB]/80 overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                style={{ background: COLORS[i] }}
                initial={{ width: 0 }}
                whileInView={{ width: `${total ? (d.value / total) * 100 : 0}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.9, delay: 0.15 + i * 0.08, ease: EASE_OUT }}
              />
            </div>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
