import * as React from 'react';
import * as ProgressPrimitive from '@radix-ui/react-progress';
import { cn } from '@/lib/utils';

interface ProgressProps
  extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> {
  value?: number;
  colorClass?: string;
}

export function Progress({ className, value = 0, colorClass, ...props }: ProgressProps) {
  const barColor = colorClass ?? (
    value >= 70 ? 'bg-[#12B76A]' :
    value >= 40 ? 'bg-[#263B80]' :
    value >= 20 ? 'bg-[#F79009]' :
    'bg-[#F04438]'
  );

  return (
    <ProgressPrimitive.Root
      className={cn('relative h-1.5 w-full overflow-hidden rounded-full bg-[#E5E7EB]', className)}
      {...props}
      value={value}
    >
      <ProgressPrimitive.Indicator
        className={cn('h-full rounded-full transition-all duration-500', barColor)}
        style={{ transform: `translateX(-${100 - value}%)` }}
      />
    </ProgressPrimitive.Root>
  );
}
