import React from 'react'
import { cn } from '@/lib/utils'

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning' | 'critical'
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
        {
          'bg-brand-purple/20 text-brand-purple-light': variant === 'default',
          'bg-bg-tertiary text-text-secondary': variant === 'secondary',
          'bg-status-critical/20 text-status-critical': variant === 'destructive',
          'border border-brand-purple/40 text-brand-purple': variant === 'outline',
          'bg-status-success/20 text-status-success': variant === 'success',
          'bg-status-warning/20 text-status-warning': variant === 'warning',
          'bg-status-critical/20 text-status-critical': variant === 'critical',
        },
        className
      )}
      {...props}
    />
  )
)
Badge.displayName = 'Badge'

export { Badge }
