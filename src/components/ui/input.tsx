import * as React from 'react';
import { cn } from '@/lib/utils';

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, type = 'text', ...props }, ref) => (
  <input
    type={type}
    ref={ref}
    className={cn(
      'flex h-9 w-full rounded-md border border-[#E7E8EC] bg-white px-3 py-1.5 text-sm text-[#172033] placeholder:text-[#9CA3AF]',
      'focus:outline-none focus:ring-2 focus:ring-[#263B80]/20 focus:border-[#263B80]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'transition-colors',
      className
    )}
    {...props}
  />
));
Input.displayName = 'Input';

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      'flex w-full rounded-md border border-[#E7E8EC] bg-white px-3 py-2 text-sm text-[#172033] placeholder:text-[#9CA3AF]',
      'focus:outline-none focus:ring-2 focus:ring-[#263B80]/20 focus:border-[#263B80]',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'resize-none transition-colors',
      className
    )}
    {...props}
  />
));
Textarea.displayName = 'Textarea';

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

export function Label({ className, required, children, ...props }: LabelProps) {
  return (
    <label
      className={cn('block text-sm font-medium text-[#172033] mb-1', className)}
      {...props}
    >
      {children}
      {required && <span className="text-[#F04438] ml-0.5">*</span>}
    </label>
  );
}

export function FormField({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('space-y-1', className)}>{children}</div>;
}

export function FormError({ message }: { message?: string }) {
  if (!message) return null;
  return <p className="text-xs text-[#B42318] mt-1">{message}</p>;
}
