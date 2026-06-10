'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, Skeleton } from '@/components/ui'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { cn } from '@/lib/utils'

interface KPICardProps {
  title: string
  value: string | number
  unit?: string
  icon: React.ReactNode
  trend?: number
  color?: 'purple' | 'blue' | 'green' | 'red'
  isLoading?: boolean
  description?: string
}

export function KPICard({
  title,
  value,
  unit,
  icon,
  trend,
  color = 'purple',
  isLoading = false,
  description,
}: KPICardProps) {
  const colorClasses = {
    purple: 'from-brand-purple/20 to-brand-purple-light/10',
    blue: 'from-blue-500/20 to-blue-400/10',
    green: 'from-status-success/20 to-green-400/10',
    red: 'from-status-critical/20 to-red-400/10',
  }

  const iconColorClasses = {
    purple: 'bg-brand-purple/20 text-brand-purple-light',
    blue: 'bg-blue-500/20 text-blue-400',
    green: 'bg-status-success/20 text-status-success',
    red: 'bg-status-critical/20 text-status-critical',
  }

  return (
    <Card className={`bg-gradient-to-br ${colorClasses[color]}`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={cn('p-2 rounded-lg', iconColorClasses[color])}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <>
            <Skeleton className="h-8 w-24 mb-2" />
            <Skeleton className="h-4 w-32" />
          </>
        ) : (
          <>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-text-primary">{value}</span>
              {unit && <span className="text-sm text-text-secondary">{unit}</span>}
            </div>
            <div className="flex items-center gap-2 mt-2">
              {trend !== undefined && (
                <>
                  {trend > 0 ? (
                    <ArrowUpRight className="w-4 h-4 text-status-success" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-status-critical" />
                  )}
                  <span
                    className={cn(
                      'text-xs font-semibold',
                      trend > 0 ? 'text-status-success' : 'text-status-critical'
                    )}
                  >
                    {Math.abs(trend)}% vs última semana
                  </span>
                </>
              )}
              {description && !trend && (
                <span className="text-xs text-text-secondary">{description}</span>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
