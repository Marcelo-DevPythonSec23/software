'use client'

import React, { useState } from 'react'
import { MainLayout } from '@/components/layouts/MainLayout'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Skeleton,
} from '@/components/ui'
import { CustomBarChart } from '@/components/charts/CustomBarChart'
import { useModelStatus, useTrainModel, useAnomalies } from '@/hooks/useML'
import { AlertTriangle, Brain, PlayCircle, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'

export default function MLPage() {
  const { data: modelStatus, isLoading: statusLoading, refetch } = useModelStatus()
  const { mutate: trainModel, isPending: isTraining } = useTrainModel()
  const { data: anomalies, isLoading: anomaliesLoading } = useAnomalies()

  const handleTrain = () => {
    toast.loading('Iniciando treinamento do modelo...')
    trainModel(500, {
      onSuccess: () => {
        toast.success('Modelo treinado com sucesso!')
        refetch()
      },
      onError: () => {
        toast.error('Erro ao treinar modelo')
      },
    })
  }

  const handleRefresh = () => {
    refetch()
    toast.success('Status atualizado')
  }

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Machine Learning</h1>
          <p className="text-text-secondary mt-2">
            Treine modelos de detecção de anomalias e clustering
          </p>
        </div>

        {/* Model Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-brand-purple" />
                Status do Modelo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {statusLoading ? (
                <>
                  <Skeleton className="h-6 w-32" />
                  <Skeleton className="h-6 w-32" />
                </>
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-text-secondary">Modelo Carregado:</span>
                    <Badge
                      variant={modelStatus?.model_loaded ? 'success' : 'destructive'}
                    >
                      {modelStatus?.model_loaded ? 'Sim' : 'Não'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-text-secondary">Modelo Treinado:</span>
                    <Badge
                      variant={modelStatus?.model_trained ? 'success' : 'warning'}
                    >
                      {modelStatus?.model_trained ? 'Sim' : 'Não'}
                    </Badge>
                  </div>
                  {modelStatus?.last_training && (
                    <div className="flex items-center justify-between">
                      <span className="text-text-secondary">Último Treinamento:</span>
                      <span className="text-sm text-text-primary">
                        {new Date(modelStatus.last_training).toLocaleDateString('pt-BR')}
                      </span>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                onClick={handleTrain}
                disabled={isTraining}
                className="w-full flex items-center justify-center gap-2"
              >
                <PlayCircle className="w-4 h-4" />
                {isTraining ? 'Treinando...' : 'Treinar Modelo'}
              </Button>
              <Button
                onClick={handleRefresh}
                variant="secondary"
                className="w-full flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Atualizar Status
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Training Stats */}
        {modelStatus?.stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-purple">
                    {modelStatus.stats.events_trained}
                  </div>
                  <p className="text-sm text-text-secondary mt-2">Eventos Treinados</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-status-critical">
                    {modelStatus.stats.anomalies_detected}
                  </div>
                  <p className="text-sm text-text-secondary mt-2">Anomalias Detectadas</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-status-warning">
                    {modelStatus.stats.anomaly_percentage.toFixed(1)}%
                  </div>
                  <p className="text-sm text-text-secondary mt-2">Taxa de Anomalias</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-brand-purple-light">
                    {modelStatus.stats.clusters}
                  </div>
                  <p className="text-sm text-text-secondary mt-2">Clusters Identificados</p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Anomalies Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-status-critical" />
              Eventos Anômalos Detectados
            </CardTitle>
          </CardHeader>
          <CardContent>
            {anomaliesLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : anomalies && anomalies.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-brand-purple/10">
                      <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                        Event ID
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                        Score
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                        Confiança
                      </th>
                      <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                        Severidade
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {anomalies.map((anomaly) => (
                      <tr
                        key={anomaly.event_id}
                        className="border-b border-brand-purple/5 hover:bg-brand-purple/5"
                      >
                        <td className="py-3 px-4 text-text-primary font-mono">
                          {anomaly.event_id.slice(0, 8)}...
                        </td>
                        <td className="py-3 px-4 text-text-secondary">
                          {anomaly.score.toFixed(2)}
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant="default">
                            {(anomaly.confidence * 100).toFixed(0)}%
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <Badge variant={anomaly.severity as any}>
                            {anomaly.severity.toUpperCase()}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-text-secondary text-center py-8">
                Nenhuma anomalia detectada
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  )
}
