'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import { motion } from 'motion/react';
import { ProjectViewModel, Supervisor } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { Avatar } from '@/components/ui/avatar';
import { getInitials, cn } from '@/lib/utils';
import { EASE_OUT } from '@/lib/motion';

const WEEKS = 16;
const WEEK_MS = 7 * 86400000;

const HEALTH = {
  ON_TRACK: { bar: 'from-[#12B76A] to-[#0E9F5C]', label: 'On track' },
  AT_RISK:  { bar: 'from-[#F79009] to-[#DC6803]', label: 'At risk' },
  DELAYED:  { bar: 'from-[#F04438] to-[#D92D20]', label: 'Delayed' },
} as const;

function startOfWeek(d: Date) {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
  return x;
}

interface Props { projects: ProjectViewModel[]; supervisors: Supervisor[] }

/** Gantt-style view of active project start→deadline across the next ~4 months. */
export function ProjectTimeline({ projects, supervisors }: Props) {
  const { rows, weeks, todayPct, from, span } = useMemo(() => {
    const now = new Date();
    const from = startOfWeek(now).getTime() - 2 * WEEK_MS;
    const span = WEEKS * WEEK_MS;
    const weeks = Array.from({ length: WEEKS }, (_, i) => new Date(from + i * WEEK_MS));
    const order = { DELAYED: 0, AT_RISK: 1, ON_TRACK: 2 };
    const rows = projects
      .filter(p => p.status === 'ACTIVE')
      .map(p => ({ p, s: new Date(p.startDate).getTime(), e: new Date(p.deadline).getTime() }))
      .filter(({ s, e }) => !Number.isNaN(s) && !Number.isNaN(e) && e >= from && s <= from + span)
      .sort((a, b) => order[a.p.health] - order[b.p.health] || a.e - b.e)
      .slice(0, 6);
    return { rows, weeks, todayPct: ((now.getTime() - from) / span) * 100, from, span };
  }, [projects]);

  const supMap = useMemo(() => Object.fromEntries(supervisors.map(s => [s.id, s])), [supervisors]);

  return (
    <GlassPanel
      title="Project Timeline"
      subtitle="Active projects, start to deadline"
      action={
        <div className="hidden sm:flex items-center gap-3 text-[11px] text-[#667085]">
          {(Object.keys(HEALTH) as (keyof typeof HEALTH)[]).map(k => (
            <span key={k} className="flex items-center gap-1.5">
              <span className={cn('w-2 h-2 rounded-full bg-gradient-to-br', HEALTH[k].bar)} />{HEALTH[k].label}
            </span>
          ))}
        </div>
      }
    >
      {rows.length === 0 ? (
        <p className="px-6 pb-8 pt-2 text-sm text-[#667085]">No active projects fall in this window.</p>
      ) : (
        <div className="overflow-x-auto px-6 pb-6">
          <div className="min-w-[640px]">
            <div className="grid grid-cols-[150px_1fr] gap-3">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-[#9CA3AF] self-end pb-1">Project</div>
              <div className="grid" style={{ gridTemplateColumns: `repeat(${WEEKS}, 1fr)` }}>
                {weeks.map((w, i) => {
                  const isNow = todayPct >= (i / WEEKS) * 100 && todayPct < ((i + 1) / WEEKS) * 100;
                  return (
                    <div key={i} className="px-0.5">
                      <div className={cn('rounded-lg text-center py-1 text-[10px] leading-tight transition-colors', isNow ? 'bg-[#2E90FA] text-white font-semibold shadow-[0_4px_10px_-3px_rgba(46,144,250,0.7)]' : 'glass-tile text-[#667085]')}>
                        {w.getDate()}<br />{w.toLocaleDateString('en-IN', { month: 'short' })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="relative mt-2 space-y-2">
              {/* grid lines + today marker */}
              <div className="absolute inset-y-0 left-[162px] right-0 pointer-events-none" aria-hidden>
                <div className="absolute inset-0 grid" style={{ gridTemplateColumns: `repeat(${WEEKS}, 1fr)` }}>
                  {weeks.map((_, i) => <div key={i} className={cn('border-l border-[#E7E8EC]/70', i % 2 && 'bg-[#E7E8EC]/20')} />)}
                </div>
                <div className="timeline-today absolute top-0 bottom-0 w-[2px]" style={{ left: `${todayPct}%` }} />
              </div>

              {rows.map(({ p, s, e }, idx) => {
                const left = Math.max(0, ((s - from) / span) * 100);
                const right = Math.min(100, ((e - from) / span) * 100);
                const sup = p.supervisorId ? supMap[p.supervisorId] : undefined;
                return (
                  <div key={p.id} className="relative grid grid-cols-[150px_1fr] gap-3 items-center h-12">
                    <Link href={`/projects/${p.id}`} className="flex items-center gap-2.5 min-w-0 rounded-xl glass-tile px-2.5 h-full hover:bg-white transition-colors">
                      <Avatar initials={sup?.avatarInitials ?? getInitials(p.name)} name={sup?.name ?? p.name} size="xs" />
                      <div className="min-w-0">
                        <div className="text-xs font-semibold text-[#172033] truncate">{p.name}</div>
                        <div className="text-[10px] text-[#9CA3AF] truncate">{p.client}</div>
                      </div>
                    </Link>
                    <div className="relative h-full">
                      <motion.div
                        initial={{ scaleX: 0, opacity: 0 }}
                        whileInView={{ scaleX: 1, opacity: 1 }}
                        viewport={{ once: true, margin: '-40px' }}
                        transition={{ duration: 0.8, delay: 0.1 + idx * 0.08, ease: EASE_OUT }}
                        style={{ left: `${left}%`, width: `${Math.max(right - left, 4)}%`, transformOrigin: 'left center' }}
                        whileHover={{ y: -2 }}
                        className={cn('absolute top-1.5 bottom-1.5 rounded-xl bg-gradient-to-r shadow-[0_8px_16px_-8px_rgba(23,32,51,0.45)] overflow-hidden', HEALTH[p.health].bar)}
                        title={`${p.name} — ${p.progress}% complete`}
                      >
                        <div className="absolute inset-y-0 left-0 bg-white/25" style={{ width: `${p.progress}%` }} />
                        <span className="relative px-2.5 text-[11px] font-semibold text-white flex items-center h-full whitespace-nowrap">{p.progress}%</span>
                      </motion.div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </GlassPanel>
  );
}
