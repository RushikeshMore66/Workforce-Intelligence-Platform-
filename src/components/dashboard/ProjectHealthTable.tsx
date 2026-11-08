'use client';

import Link from 'next/link';
import { motion } from 'motion/react';
import { ArrowRight } from 'lucide-react';
import { Project, Supervisor } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { cn, daysUntil } from '@/lib/utils';
import { EASE_OUT, slideX, stagger } from '@/lib/motion';

interface Props { projects: Project[]; supervisors: Supervisor[] }

const HEALTH = {
  ON_TRACK: { chip: 'bg-[#ECFDF3] text-[#027A48]', bar: 'bg-[#12B76A]', label: 'On track' },
  AT_RISK:  { chip: 'bg-[#FFFAEB] text-[#B54708]', bar: 'bg-[#F79009]', label: 'At risk' },
  DELAYED:  { chip: 'bg-[#FEF3F2] text-[#B42318]', bar: 'bg-[#F04438]', label: 'Delayed' },
} as const;

export function ProjectHealthTable({ projects, supervisors }: Props) {
  const supMap = Object.fromEntries(supervisors.map(s => [s.id, s]));
  const order = { DELAYED: 0, AT_RISK: 1, ON_TRACK: 2 };
  const top = projects.filter(p => p.status === 'ACTIVE').sort((a, b) => order[a.health] - order[b.health]).slice(0, 6);

  return (
    <GlassPanel
      title="Project Health"
      subtitle="Most urgent active projects first"
      action={
        <Link href="/projects" className="group glass-pill rounded-full h-8 px-3 text-xs font-medium text-[#172033] flex items-center gap-1.5 hover:bg-white transition">
          View all <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-0.5" />
        </Link>
      }
      bodyClassName="px-3 pb-3"
    >
      {top.length === 0 ? (
        <p className="p-6 text-sm text-[#667085] text-center">No active projects found.</p>
      ) : (
        <motion.ul variants={stagger(0.05, 0.1)} initial="hidden" whileInView="show" viewport={{ once: true }} className="space-y-1">
          {top.map((proj, i) => {
            const sup = proj.supervisorId ? supMap[proj.supervisorId] : undefined;
            const daysLeft = daysUntil(proj.deadline);
            const h = HEALTH[proj.health];
            return (
              <motion.li key={proj.id} variants={slideX}>
                <Link href={`/projects/${proj.id}`} className="flex items-center gap-4 rounded-2xl px-3 py-3 hover:bg-white/80 hover:shadow-[0_6px_16px_-10px_rgba(23,32,51,0.25)] transition group">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-[#172033] truncate group-hover:text-[#263B80] transition-colors">{proj.name}</div>
                    <div className="text-xs text-[#667085] mt-0.5 truncate">{proj.client}{sup ? ` · ${sup.name}` : ''}</div>
                  </div>
                  <div className="flex items-center gap-2 w-[130px]">
                    <div className="relative h-1.5 flex-1 rounded-full bg-[#E5E7EB] overflow-hidden" role="progressbar" aria-valuenow={proj.progress} aria-valuemin={0} aria-valuemax={100}>
                      <motion.div
                        className={cn('absolute inset-y-0 left-0 rounded-full', h.bar)}
                        initial={{ width: 0 }}
                        whileInView={{ width: `${proj.progress}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.9, delay: 0.2 + i * 0.06, ease: EASE_OUT }}
                      />
                    </div>
                    <span className="text-xs font-semibold text-[#172033] w-8 text-right tabular-nums">{proj.progress}%</span>
                  </div>
                  <span className={cn('hidden sm:inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold', h.chip)}>{h.label}</span>
                  <span className={cn('text-xs font-medium w-14 text-right tabular-nums', daysLeft < 30 ? 'text-[#B54708]' : 'text-[#667085]')}>
                    {daysLeft > 0 ? `${daysLeft}d` : 'Overdue'}
                  </span>
                </Link>
              </motion.li>
            );
          })}
        </motion.ul>
      )}
    </GlassPanel>
  );
}
