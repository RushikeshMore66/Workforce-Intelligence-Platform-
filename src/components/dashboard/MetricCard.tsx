import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    label: string;
    positive?: boolean;
  };
  variant?: 'default' | 'warning' | 'danger' | 'success';
  className?: string;
}

export function MetricCard({
  title, value, subtitle, icon: Icon,
  trend, variant = 'default', className,
}: MetricCardProps) {
  const valueColor = {
    default: 'text-[#172033]',
    success: 'text-[#027A48]',
    warning: 'text-[#B54708]',
    danger:  'text-[#B42318]',
  }[variant];

  return (
    <div className={cn(
      'bg-white border border-[#E7E8EC] rounded-xl p-5 flex flex-col gap-3',
      'shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]',
      className
    )}>
      <div className="flex items-start justify-between gap-2">
        <span className="text-xs font-semibold text-[#667085] uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-[#EEF1FA] flex items-center justify-center flex-shrink-0">
            <Icon className="w-4 h-4 text-[#263B80]" />
          </div>
        )}
      </div>
      <div>
        <div className={cn('text-[2rem] font-bold leading-none font-variant-numeric tabular-nums', valueColor)}>
          {value}
        </div>
        {subtitle && (
          <div className="text-xs text-[#9CA3AF] mt-1.5">{subtitle}</div>
        )}
        {trend && (
          <div className={cn(
            'text-xs font-medium mt-1.5',
            trend.positive ? 'text-[#027A48]' : 'text-[#B54708]'
          )}>
            {trend.label}
          </div>
        )}
      </div>
    </div>
  );
}
