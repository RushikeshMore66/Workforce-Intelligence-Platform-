import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium ring-1 ring-inset transition-colors',
  {
    variants: {
      variant: {
        default:   'bg-neutral-100 text-neutral-700 ring-neutral-200',
        primary:   'bg-[#EEF1FA] text-[#263B80] ring-[#c7d0f0]',
        success:   'bg-[#ECFDF3] text-[#027A48] ring-[#ABEFC6]',
        warning:   'bg-[#FFFAEB] text-[#B54708] ring-[#FEDF89]',
        danger:    'bg-[#FEF3F2] text-[#B42318] ring-[#FECDCA]',
        info:      'bg-[#EFF8FF] text-[#1849A9] ring-[#B2DDFF]',
        gold:      'bg-[#FBF5E8] text-[#B08A3E] ring-[#e8d9be]',
        outline:   'bg-white text-neutral-600 ring-neutral-300',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  dot?: boolean;
}

export function Badge({ className, variant, dot, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      {dot && (
        <span
          className={cn(
            'inline-block w-1.5 h-1.5 rounded-full',
            variant === 'success' && 'bg-[#12B76A]',
            variant === 'warning' && 'bg-[#F79009]',
            variant === 'danger'  && 'bg-[#F04438]',
            variant === 'info'    && 'bg-[#2E90FA]',
            variant === 'primary' && 'bg-[#263B80]',
            variant === 'gold'    && 'bg-[#B08A3E]',
            (!variant || variant === 'default' || variant === 'outline') && 'bg-neutral-400',
          )}
        />
      )}
      {children}
    </span>
  );
}
