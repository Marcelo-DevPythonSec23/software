'use client'

import React from 'react'
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'

interface SeverityDistributionChartProps {
  data: {
    critical: number
    high: number
    medium: number
    low: number
  }
  isLoading?: boolean
}

const COLORS: Record<string, string> = {
  critical: '#EF4444',
  high: '#F97316',
  medium: '#F59E0B',
  low: '#10B981',
}

const SEVERITY_LABELS: Record<string, string> = {
  critical: 'Crítico',
  high: 'Alto',
  medium: 'Médio',
  low: 'Baixo',
}

export function SeverityDistributionChart({
  data,
  isLoading,
}: SeverityDistributionChartProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Distribuição de Severidade</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80 bg-bg-tertiary rounded-lg animate-pulse" />
        </CardContent>
      </Card>
    )
  }

  const chartData = Object.entries(data)
    .map(([key, value]) => ({
      name: SEVERITY_LABELS[key],
      value,
      fill: COLORS[key],
    }))
    .filter((item) => item.value > 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuição de Severidade</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }) => `${name}: ${value}`}
              outerRadius={100}
              fill="#8B5CF6"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#111827',
                border: '1px solid #7C3AED',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#F8FAFC' }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
