'use client';

import * as React from 'react';
import { motion, type HTMLMotionProps } from 'motion/react';
import { cn } from '@/lib/utils';
import { rise } from '@/lib/motion';

interface PanelProps extends HTMLMotionProps<'section'> {
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
  bodyClassName?: string;
}

/** Frosted card used by every dashboard widget. Enters via the parent's stagger. */
export function GlassPanel({ title, subtitle, action, bodyClassName, className, children, ...rest }: PanelProps) {
  return (
    <motion.section
      variants={rise}
      className={cn('glass rounded-[24px] overflow-hidden', className)}
      {...rest}
    >
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 px-6 pt-5 pb-3">
          <div className="min-w-0">
            {title && <h2 className="text-[15px] font-semibold tracking-tight text-[#172033]">{title}</h2>}
            {subtitle && <p className="text-xs text-[#667085] mt-0.5">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className={bodyClassName}>{children as React.ReactNode}</div>
    </motion.section>
  );
}
