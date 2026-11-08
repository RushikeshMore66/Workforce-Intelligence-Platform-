'use client';

import Link from 'next/link';
import { motion } from 'motion/react';
import { ArrowUpRight, FolderKanban, FileText, Users, Sparkles } from 'lucide-react';
import { rise, spring } from '@/lib/motion';
import { useAuth } from '@/lib/auth/useAuth';
import { canAccessSection } from '@/lib/auth/rbac';
import { AnimatedNumber } from '@/components/ui/animated-number';

interface Props {
  attentionCount: number;
  blocked: number;
  atRisk: number;
}

const ACTIONS = [
  { label: 'Projects', href: '/projects', icon: FolderKanban },
  { label: 'Workforce', href: '/workforce', icon: Users },
  { label: 'Reports', href: '/reports', icon: FileText },
  { label: 'Intelligence', href: '/intelligence', icon: Sparkles },
];

/** Focus card: a glowing orb, today's headline number and one-click navigation. */
export function HeroInsight({ attentionCount, blocked, atRisk }: Props) {
  const { user } = useAuth();
  const actions = ACTIONS.filter(a => canAccessSection(user?.role, a.href));
  const calm = attentionCount === 0 && blocked === 0 && atRisk === 0;

  return (
    <motion.section variants={rise} className="glass rounded-[24px] p-6 h-full flex flex-col items-center text-center relative overflow-hidden">
      <div className="pointer-events-none absolute inset-x-0 -top-24 h-64 bg-[radial-gradient(closest-side,rgba(76,128,240,0.22),transparent)]" />
      <div className="relative mt-2 mb-5">
        <div className="orb w-24 h-24 rounded-full" aria-hidden />
        <div className="absolute inset-x-3 -bottom-3 h-3 rounded-full bg-[#263B80]/20 blur-md" aria-hidden />
      </div>

      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#9CA3AF]">Today&apos;s focus</p>
      <div className="mt-1 flex items-baseline gap-2">
        <AnimatedNumber value={attentionCount} className="text-5xl font-bold tracking-tight text-[#172033] tabular-nums" />
        <span className="text-sm text-[#667085]">{attentionCount === 1 ? 'item needs you' : 'items need you'}</span>
      </div>
      <p className="text-sm text-[#667085] mt-2 max-w-[260px]">
        {calm
          ? 'Everything is on track. Nothing needs your attention right now.'
          : `${blocked} blocked task${blocked === 1 ? '' : 's'} and ${atRisk} project${atRisk === 1 ? '' : 's'} at risk.`}
      </p>

      <div className="mt-auto pt-6 grid grid-cols-2 gap-2 w-full">
        {actions.map(({ label, href, icon: Icon }) => (
          <motion.div key={href} whileHover={{ y: -2 }} whileTap={{ scale: 0.96 }} transition={spring}>
            <Link
              href={href}
              className="glass-pill rounded-full h-10 px-3.5 flex items-center justify-between gap-2 text-[13px] font-medium text-[#172033] hover:bg-white transition-colors group"
            >
              <span className="flex items-center gap-2"><Icon className="w-3.5 h-3.5 text-[#667085]" />{label}</span>
              <ArrowUpRight className="w-3.5 h-3.5 text-[#9CA3AF] group-hover:text-[#172033] group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
            </Link>
          </motion.div>
        ))}
      </div>
    </motion.section>
  );
}
