'use client';

import { RefreshCw } from 'lucide-react';
import { motion } from 'motion/react';
import { rise } from '@/lib/motion';
import { cn } from '@/lib/utils';

export function SectionError({ message, onRetry, className }: { message: string; onRetry: () => void; className?: string }) {
  return (
    <motion.div
      variants={rise}
      role="alert"
      className={cn('glass rounded-[24px] p-6 text-center flex flex-col items-center justify-center min-h-[160px]', className)}
    >
      <p className="text-sm text-[#B42318] mb-3">{message}</p>
      <button
        onClick={onRetry}
        className="inline-flex items-center gap-2 h-9 px-4 text-sm font-medium text-[#172033] glass-pill rounded-full hover:bg-white active:scale-95 transition"
      >
        <RefreshCw className="w-3.5 h-3.5" /> Retry
      </button>
    </motion.div>
  );
}
