'use client'

import React, { useState, useEffect } from 'react'
import { MainLayout } from '@/components/layouts/MainLayout'
import { KPICard } from '@/components/dashboard/KPICard'
import { StatsSummary } from '@/components/dashboard/StatsSummary'
import { TimeSeriesChart } from '@/components/charts/TimeSeriesChart'
import { SeverityDistributionChart } from '@/components/charts/SeverityDistributionChart'
import { EventsTable } from '@/components/tables/EventsTable'
import { IOCTable } from '@/components/tables/IOCTable'
import {
  Activity,
  AlertTriangle,
  Network,
  TrendingUp,
  Zap,
} from 'lucide-react'
import { useEvents, useEventCount, useEventsBySeverity } from '@/hooks/useEvents'
import { useCorrelation, useReusedIOCs } from '@/hooks/useCorrelation'
import { useModelStatus } from '@/hooks/useML'

export default function DashboardPage() {
  const { data: events, isLoading: eventsLoading } = useEvents({ limit: 50 })
  const { data: eventCount, isLoading: countLoading } = useEventCount()
  const { data: severityData, isLoading: severityLoading } = useEventsBySeverity()
  const { data: correlationData, isLoading: correlationLoading } = useCorrelation()
  const { data: reusedIOCs, isLoading: iocLoading } = useReusedIOCs()
  const { data: modelStatus, isLoading: modelLoading } = useModelStatus()

  const criticalEvents = severityData?.critical || 0
  const totalIOCs = correlationData?.total_reused_iocs || 0
  const anomalyRate = modelStatus?.stats?.anomaly_percentage || 0

  // Generate mock time series data
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([])

  useEffect(() => {
    // Mock data for timeline
    const now = new Date()
    const data = Array.from({ length: 24 }).map((_, i) => ({
      timestamp: new Date(now.getTime() - (23 - i) * 3600000)
        .toLocaleTimeString('pt-BR', { hour: '2-digit' }),
      count: Math.floor(Math.random() * 50) + 10,
    }))
    setTimeSeriesData(data)
  }, [])

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Dashboard</h1>
          <p className="text-text-secondary mt-2">
            Análise em tempo real de eventos de segurança e ameaças
          </p>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            title="Total de Eventos"
            value={eventCount || 0}
            icon={<Activity className="w-5 h-5" />}
            color="purple"
            isLoading={countLoading}
            trend={12}
          />
          <KPICard
            title="Eventos Críticos"
            value={criticalEvents}
            icon={<AlertTriangle className="w-5 h-5" />}
            color="red"
            isLoading={severityLoading}
            trend={-5}
          />
          <KPICard
            title="IOCs Detectados"
            value={totalIOCs}
            icon={<Network className="w-5 h-5" />}
            color="blue"
            isLoading={correlationLoading}
            trend={8}
          />
          <KPICard
            title="Taxa de Anomalias"
            value={anomalyRate.toFixed(1)}
            unit="%"
            icon={<Zap className="w-5 h-5" />}
            color="green"
            isLoading={modelLoading}
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <TimeSeriesChart
              data={timeSeriesData}
              title="Timeline de Eventos (24h)"
              isLoading={eventsLoading}
            />
          </div>
          <SeverityDistributionChart
            data={severityData || { critical: 0, high: 0, medium: 0, low: 0 }}
            isLoading={severityLoading}
          />
        </div>

        {/* Stats Summary */}
        <StatsSummary
          totalEvents={eventCount || 0}
          criticalEvents={criticalEvents}
          detectedIOCs={totalIOCs}
          anomalyRate={anomalyRate}
          isLoading={severityLoading}
        />

        {/* Tables Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <EventsTable
            events={events?.items || []}
            isLoading={eventsLoading}
          />
          <IOCTable
            iocs={reusedIOCs || []}
            isLoading={iocLoading}
          />
        </div>
      </div>
    </MainLayout>
  )
}
