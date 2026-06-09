'use client'

import React from 'react'
import { MainLayout } from '@/components/layouts/MainLayout'
import { Card, CardContent, CardHeader, CardTitle, Button, Badge } from '@/components/ui'
import { Download, FileText, AlertCircle } from 'lucide-react'
import { useEvents } from '@/hooks/useEvents'
import { useCorrelation } from '@/hooks/useCorrelation'
import { toast } from 'sonner'

export default function ReportsPage() {
  const { data: events } = useEvents({ limit: 100 })
  const { data: correlation } = useCorrelation()

  const handleGenerateReport = (type: 'summary' | 'correlation' | 'ml') => {
    toast.loading('Gerando relatório...')
    setTimeout(() => {
      toast.success(`Relatório ${type} gerado com sucesso!`)
    }, 2000)
  }

  const reports = [
    {
      title: 'Resumo Executivo',
      description: 'Visão geral dos principais indicadores e descobertas',
      type: 'summary' as const,
      icon: <FileText className="w-5 h-5" />,
    },
    {
      title: 'Análise de Correlação',
      description: 'Detalhes de IOCs reutilizados e padrões identificados',
      type: 'correlation' as const,
      icon: <AlertCircle className="w-5 h-5" />,
    },
    {
      title: 'Análise de Anomalias',
      description: 'Eventos anômalos detectados pelo modelo ML',
      type: 'ml' as const,
      icon: <AlertCircle className="w-5 h-5" />,
    },
  ]

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Relatórios</h1>
          <p className="text-text-secondary mt-2">
            Gere relatórios profissionais em HTML e PDF para análise forense
          </p>
        </div>

        {/* Report Generation */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {reports.map((report) => (
            <Card key={report.type} className="flex flex-col">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{report.title}</CardTitle>
                  <div className="text-brand-purple">{report.icon}</div>
                </div>
              </CardHeader>
              <CardContent className="flex-1 space-y-4">
                <p className="text-text-secondary text-sm">{report.description}</p>
                <Button
                  onClick={() => handleGenerateReport(report.type)}
                  className="w-full flex items-center justify-center gap-2"
                  variant="default"
                >
                  <Download className="w-4 h-4" />
                  Gerar Relatório
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Reports */}
        <Card>
          <CardHeader>
            <CardTitle>Relatórios Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 rounded-lg bg-bg-tertiary hover:bg-brand-purple/5 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    <FileText className="w-4 h-4 text-brand-purple" />
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        Relatório #{5 - i} - 2026-06-0{7 - i}
                      </p>
                      <p className="text-xs text-text-secondary">
                        Gerado em {new Date(Date.now() - i * 86400000).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="success">Completo</Badge>
                    <Button variant="ghost" size="sm">
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Report Preview */}
        <Card>
          <CardHeader>
            <CardTitle>Preview - Resumo Executivo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-bg-tertiary rounded-lg p-6 space-y-4 max-h-96 overflow-y-auto">
              <div>
                <h3 className="text-lg font-semibold text-text-primary">
                  Relatório de Análise de Segurança
                </h3>
                <p className="text-sm text-text-secondary mt-2">
                  Período: Últimas 24 horas
                </p>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <p className="font-semibold text-text-primary">Principais Descobertas:</p>
                  <ul className="list-disc list-inside mt-2 text-text-secondary space-y-1">
                    <li>Detectados {events?.items?.length || 0} eventos de segurança</li>
                    <li>Taxa de anomalia de {(5.2).toFixed(1)}%</li>
                    <li>
                      {correlation?.total_reused_iocs || 0} IOCs únicos identificados
                    </li>
                  </ul>
                </div>

                <div>
                  <p className="font-semibold text-text-primary">Recomendações:</p>
                  <ul className="list-disc list-inside mt-2 text-text-secondary space-y-1">
                    <li>Investigar eventos com severidade crítica prioritariamente</li>
                    <li>Correlacionar dados com inteligência externa</li>
                    <li>Implementar alertas para anomalias detectadas</li>
                  </ul>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
