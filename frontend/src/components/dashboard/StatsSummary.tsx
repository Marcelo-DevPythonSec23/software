'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Badge } from '@/components/ui'
import { formatNumber } from '@/lib/utils'

interface StatsSummaryProps {
  totalEvents: number
  criticalEvents: number
  detectedIOCs: number
  anomalyRate: number
  isLoading?: boolean
}

export function StatsSummary({
  totalEvents,
  criticalEvents,
  detectedIOCs,
  anomalyRate,
  isLoading,
}: StatsSummaryProps) {
  const stats = [
    {
      label: 'Total de Eventos',
      value: formatNumber(totalEvents),
      color: 'default',
    },
    {
      label: 'Eventos Críticos',
      value: formatNumber(criticalEvents),
      color: 'critical',
    },
    {
      label: 'IOCs Detectados',
      value: formatNumber(detectedIOCs),
      color: 'warning',
    },
    {
      label: 'Taxa de Anomalias',
      value: `${anomalyRate.toFixed(1)}%`,
      color: 'warning',
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resumo Estatístico</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map((stat, idx) => (
            <div key={idx} className="flex flex-col gap-2">
              <span className="text-sm text-text-secondary">{stat.label}</span>
              <span className="text-2xl font-bold text-text-primary">{stat.value}</span>
              <Badge variant={stat.color as any}>
                {idx === 3 ? 'Análise' : 'Ativo'}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
