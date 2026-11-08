'use client';

import Link from 'next/link';
import { motion } from 'motion/react';
import { AlertTriangle, Clock, ShieldAlert, Zap, Eye, ChevronRight, CheckCircle2 } from 'lucide-react';
import { AttentionItem } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { slideX, stagger } from '@/lib/motion';

const TYPE_CONFIG = {
  DEADLINE: { icon: Clock,         chip: 'bg-[#FFFAEB] text-[#B54708]' },
  BLOCKER:  { icon: ShieldAlert,   chip: 'bg-[#FEF3F2] text-[#B42318]' },
  RISK:     { icon: AlertTriangle, chip: 'bg-[#FEF3F2] text-[#B42318]' },
  OVERLOAD: { icon: Zap,           chip: 'bg-[#FFFAEB] text-[#B54708]' },
  REVIEW:   { icon: Eye,           chip: 'bg-[#EFF8FF] text-[#1849A9]' },
} as const;

const PRIORITY = {
  HIGH:   { dot: 'bg-[#F04438]', label: 'High' },
  MEDIUM: { dot: 'bg-[#F79009]', label: 'Medium' },
  LOW:    { dot: 'bg-[#12B76A]', label: 'Low' },
} as const;

export function AttentionRequired({ items }: { items: AttentionItem[] }) {
  return (
    <GlassPanel
      title="Attention Required"
      subtitle={items.length ? `${items.length} item${items.length === 1 ? '' : 's'} need your review` : 'All clear'}
      bodyClassName="px-3 pb-3"
    >
      {items.length === 0 ? (
        <div className="flex flex-col items-center gap-2 py-8 text-center text-sm text-[#667085]">
          <CheckCircle2 className="w-8 h-8 text-[#12B76A]" />
          Nothing needs your attention.
        </div>
      ) : (
        <motion.ul variants={stagger(0.06, 0.1)} initial="hidden" whileInView="show" viewport={{ once: true }} className="space-y-1.5 max-h-[420px] overflow-y-auto">
          {items.map(item => {
            const cfg = TYPE_CONFIG[item.type];
            const pr = PRIORITY[item.priority];
            const Icon = cfg.icon;
            return (
              <motion.li key={item.id} variants={slideX} whileHover={{ x: 3 }} className="rounded-2xl glass-tile p-3 flex items-start gap-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${cfg.chip}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-[13px] font-semibold text-[#172033] leading-snug">{item.title}</div>
                      <div className="text-xs text-[#667085] mt-0.5 line-clamp-2">{item.description}</div>
                    </div>
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${pr.dot}`} title={`${pr.label} priority`} aria-label={`${pr.label} priority`} />
                  </div>
                  {item.projectId && (
                    <Link href={`/projects/${item.projectId}`} className="inline-flex items-center gap-0.5 text-xs text-[#263B80] hover:gap-1.5 mt-1.5 font-semibold transition-all">
                      View project <ChevronRight className="w-3 h-3" />
                    </Link>
                  )}
                </div>
              </motion.li>
            );
          })}
        </motion.ul>
      )}
    </GlassPanel>
  );
}
