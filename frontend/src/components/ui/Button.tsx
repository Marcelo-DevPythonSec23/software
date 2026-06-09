import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default:
          'bg-brand-purple hover:bg-brand-purple-dark text-white shadow-lg hover:shadow-purple-glow',
        secondary:
          'bg-bg-tertiary hover:bg-bg-secondary text-text-primary border border-brand-purple/20 hover:border-brand-purple/40',
        danger:
          'bg-status-critical hover:bg-red-600 text-white shadow-lg',
        success:
          'bg-status-success hover:bg-green-600 text-white shadow-lg',
        ghost: 'hover:bg-bg-tertiary text-text-primary',
        outline:
          'border border-brand-purple/40 bg-transparent hover:bg-brand-purple/5 text-brand-purple',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-12 rounded-lg px-6',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props}
    />
  )
)
Button.displayName = 'Button'

export { Button, buttonVariants }
