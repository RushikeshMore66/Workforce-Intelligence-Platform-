'use client';

import { motion } from 'motion/react';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { rise, spring } from '@/lib/motion';
import { AnimatedNumber } from '@/components/ui/animated-number';

interface MetricCardProps {
  title: string;
  value: number;
  subtitle?: string;
  icon?: LucideIcon;
  variant?: 'default' | 'warning' | 'danger' | 'success';
  className?: string;
}

const TONE = {
  default: { chip: 'bg-[#EEF1FA] text-[#263B80]', value: 'text-[#172033]', glow: 'from-[#263B80]/10' },
  success: { chip: 'bg-[#ECFDF3] text-[#027A48]', value: 'text-[#172033]', glow: 'from-[#12B76A]/12' },
  warning: { chip: 'bg-[#FFFAEB] text-[#B54708]', value: 'text-[#172033]', glow: 'from-[#F79009]/14' },
  danger:  { chip: 'bg-[#FEF3F2] text-[#B42318]', value: 'text-[#172033]', glow: 'from-[#F04438]/12' },
};

export function MetricCard({ title, value, subtitle, icon: Icon, variant = 'default', className }: MetricCardProps) {
  const tone = TONE[variant];
  return (
    <motion.div
      variants={rise}
      whileHover={{ y: -4 }}
      transition={spring}
      className={cn('glass relative rounded-[22px] p-5 overflow-hidden group', className)}
    >
      <div className={cn('pointer-events-none absolute -top-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br to-transparent opacity-70 group-hover:scale-125 transition-transform duration-500', tone.glow)} />
      <div className="relative flex items-start justify-between gap-2">
        <span className="text-[11px] font-semibold text-[#667085] uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={cn('w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:rotate-[8deg] group-hover:scale-110', tone.chip)}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="relative mt-4">
        <AnimatedNumber value={value} className={cn('text-[34px] font-bold leading-none tabular-nums tracking-tight', tone.value)} />
        {subtitle && <div className="text-xs text-[#9CA3AF] mt-2">{subtitle}</div>}
      </div>
    </motion.div>
  );
}
