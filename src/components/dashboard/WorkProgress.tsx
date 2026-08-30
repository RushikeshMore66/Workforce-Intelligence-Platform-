'use client';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

interface Props {
  completed: number;
  inProgress: number;
  pending: number;
  blocked: number;
}

const COLORS = ['#12B76A', '#263B80', '#9CA3AF', '#F04438'];

export function WorkProgress({ completed, inProgress, pending, blocked }: Props) {
  const data = [
    { name: 'Completed',   value: completed },
    { name: 'In Progress', value: inProgress },
    { name: 'Pending',     value: pending },
    { name: 'Blocked',     value: blocked },
  ];
  const total = completed + inProgress + pending + blocked;

  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <div className="px-5 py-4 border-b border-[#E7E8EC]">
        <h2 className="text-sm font-semibold text-[#172033]">Work Progress</h2>
        <p className="text-xs text-[#667085] mt-0.5">{total} total work items</p>
      </div>
      <div className="p-5 flex flex-col sm:flex-row items-center gap-4">
        <div className="w-full sm:w-48 h-40">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%" cy="50%"
                innerRadius={48}
                outerRadius={70}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ border: '1px solid #E7E8EC', borderRadius: 8, fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-1 space-y-2.5 w-full">
          {data.map((d, i) => (
            <div key={d.name} className="flex items-center gap-3">
              <span className="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: COLORS[i] }} />
              <div className="flex-1 flex items-center justify-between gap-2">
                <span className="text-xs text-[#667085]">{d.name}</span>
                <div className="flex items-center gap-2">
                  <div className="h-1 w-16 rounded-full bg-[#E5E7EB] overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${(d.value / total) * 100}%`, background: COLORS[i] }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-[#172033] w-8 text-right">{d.value}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
