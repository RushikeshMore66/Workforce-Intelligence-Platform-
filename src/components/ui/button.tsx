import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#263B80] focus-visible:ring-offset-1 disabled:pointer-events-none disabled:opacity-50 whitespace-nowrap',
  {
    variants: {
      variant: {
        primary:   'bg-[#263B80] text-white hover:bg-[#1e2f66] active:bg-[#192860]',
        secondary: 'bg-white text-[#172033] border border-[#E7E8EC] hover:bg-[#F3F4F6] active:bg-[#E5E7EB]',
        ghost:     'text-[#667085] hover:bg-[#F3F4F6] hover:text-[#172033]',
        danger:    'bg-[#F04438] text-white hover:bg-[#d63831]',
        outline:   'border border-[#263B80] text-[#263B80] bg-transparent hover:bg-[#EEF1FA]',
        link:      'text-[#263B80] underline-offset-4 hover:underline p-0 h-auto',
      },
      size: {
        sm:   'h-7 px-2.5 text-xs rounded',
        md:   'h-8 px-3 text-sm',
        default: 'h-9 px-4',
        lg:   'h-10 px-5 text-base',
        icon: 'h-8 w-8 p-0',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="inline-block w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>{children}</span>
        </>
      ) : children}
    </button>
  )
);
Button.displayName = 'Button';
