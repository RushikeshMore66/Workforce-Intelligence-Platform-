import * as React from 'react';
import * as AvatarPrimitive from '@radix-ui/react-avatar';
import { cn } from '@/lib/utils';

// Deterministic color palette for avatar backgrounds
const AVATAR_COLORS = [
  '#263B80', '#B08A3E', '#027A48', '#B54708',
  '#1849A9', '#6941C6', '#3538CD', '#C01048',
];

function getAvatarColor(initials: string): string {
  const code = initials.charCodeAt(0) + (initials.charCodeAt(1) || 0);
  return AVATAR_COLORS[code % AVATAR_COLORS.length];
}

interface AvatarProps {
  initials: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  xs: 'w-6 h-6 text-[10px]',
  sm: 'w-8 h-8 text-xs',
  md: 'w-9 h-9 text-sm',
  lg: 'w-11 h-11 text-base',
};

export function Avatar({ initials, name, size = 'sm', className }: AvatarProps) {
  const bg = getAvatarColor(initials);
  return (
    <AvatarPrimitive.Root
      className={cn('relative inline-flex items-center justify-center rounded-full flex-shrink-0', sizeClasses[size], className)}
      style={{ backgroundColor: bg }}
      title={name}
    >
      <AvatarPrimitive.Fallback
        className="text-white font-semibold leading-none"
        delayMs={0}
      >
        {initials}
      </AvatarPrimitive.Fallback>
    </AvatarPrimitive.Root>
  );
}

export function AvatarGroup({ initials, max = 4 }: { initials: string[]; max?: number }) {
  const visible = initials.slice(0, max);
  const overflow = initials.length - max;
  return (
    <div className="flex -space-x-2">
      {visible.map((i, idx) => (
        <Avatar key={idx} initials={i} size="xs" className="ring-2 ring-white" />
      ))}
      {overflow > 0 && (
        <span className="inline-flex w-6 h-6 items-center justify-center rounded-full bg-neutral-200 text-[10px] font-medium text-neutral-600 ring-2 ring-white">
          +{overflow}
        </span>
      )}
    </div>
  );
}
