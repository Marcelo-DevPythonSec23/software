import React from 'react'
import { cn } from '@/lib/utils'

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'animate-pulse rounded-lg bg-gradient-to-r from-bg-tertiary via-bg-secondary to-bg-tertiary',
        className
      )}
      {...props}
    />
  )
)
Skeleton.displayName = 'Skeleton'

export { Skeleton }
