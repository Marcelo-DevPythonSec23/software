'use client'

import React, { useState } from 'react'
import { MainLayout } from '@/components/layouts/MainLayout'
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge } from '@/components/ui'
import { IOCTable } from '@/components/tables/IOCTable'
import { CustomBarChart } from '@/components/charts/CustomBarChart'
import { useCorrelation, useReusedIOCs, useSearchIOCDetail } from '@/hooks/useCorrelation'
import { useEvents } from '@/hooks/useEvents'
import { Search, Network, TrendingUp } from 'lucide-react'
import { toast } from 'sonner'

export default function CorrelationPage() {
  const [searchIOC, setSearchIOC] = useState('')
  const [timeWindow, setTimeWindow] = useState(3600)

  const { data: correlationData, isLoading: correlationLoading } = useCorrelation(timeWindow)
  const { data: reusedIOCs, isLoading: iocLoading } = useReusedIOCs()
  const { data: events } = useEvents({ limit: 100 })

  // Generate IPs distribution for chart
  const ipDistributionData = React.useMemo(() => {
    return reusedIOCs
      ?.slice(0, 10)
      .map((ioc) => ({
        name: ioc.ioc,
        value: ioc.occurrence_count,
      })) || []
  }, [reusedIOCs])

  const handleTimeWindowChange = (newWindow: number) => {
    setTimeWindow(newWindow)
    toast.success(`Janela temporal alterada para ${newWindow / 3600}h`)
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Correlação de Dados</h1>
          <p className="text-text-secondary mt-2">
            Identifique padrões e IOCs reutilizados em seus eventos
          </p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-sm font-medium">Total Correlacionado</CardTitle>
              <Network className="w-4 h-4 text-brand-purple" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{correlationData?.total_matched || 0}</div>
              <p className="text-xs text-text-secondary mt-2">eventos correlacionados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-sm font-medium">IOCs Únicos</CardTitle>
              <TrendingUp className="w-4 h-4 text-brand-purple-light" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{correlationData?.total_reused_iocs || 0}</div>
              <p className="text-xs text-text-secondary mt-2">indicadores detectados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-sm font-medium">Taxa de Reuso</CardTitle>
              <Badge>
                {reusedIOCs && reusedIOCs.length > 0
                  ? ((correlationData?.total_matched || 0) / (events?.items?.length || 1)).toFixed(1)
                  : '0'}
                %
              </Badge>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-text-secondary">média de correlação</p>
            </CardContent>
          </Card>
        </div>

        {/* Time Window Filter */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Configurações de Análise</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-text-primary mb-2 block">
                  Janela Temporal (segundos)
                </label>
                <div className="flex gap-2 flex-wrap">
                  {[3600, 7200, 86400].map((window) => (
                    <Button
                      key={window}
                      variant={timeWindow === window ? 'default' : 'secondary'}
                      onClick={() => handleTimeWindowChange(window)}
                      size="sm"
                    >
                      {window === 3600
                        ? '1h'
                        : window === 7200
                        ? '2h'
                        : '24h'}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Search IOC */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Buscar IOC</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative">
              <Search className="absolute left-3 top-3 w-4 h-4 text-text-secondary" />
              <Input
                placeholder="Digite um IP ou domínio..."
                value={searchIOC}
                onChange={(e) => setSearchIOC(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Charts */}
        {ipDistributionData.length > 0 && (
          <CustomBarChart
            data={ipDistributionData}
            title="Top 10 IPs Reutilizados"
            color="#8B5CF6"
            isLoading={iocLoading}
          />
        )}

        {/* IOC Table */}
        <IOCTable
          iocs={reusedIOCs || []}
          isLoading={iocLoading}
        />
      </div>
    </MainLayout>
  )
}
