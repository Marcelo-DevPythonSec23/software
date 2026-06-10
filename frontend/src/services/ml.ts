import { apiClient } from './api'
import {
  ModelStatus,
  AnomalyDetail,
  TrainingStats,
  ClusterResult,
  NormalizedEvent,
} from '@/types'

export const mlService = {
  // Get model status
  async getModelStatus() {
    const { data } = await apiClient.get<ModelStatus>('/model/status')
    return data
  },

  // Train model
  async trainModel(limit: number = 500) {
    const { data } = await apiClient.post<{
      trained: boolean
      stats?: TrainingStats
    }>('/ml/train', null, {
      params: { limit },
    })
    return data
  },

  // Score event
  async scoreEvent(event: NormalizedEvent) {
    const { data } = await apiClient.post<AnomalyDetail>('/ml/score', event)
    return data
  },

  // Cluster events
  async clusterEvents(limit: number = 100) {
    const { data } = await apiClient.get<ClusterResult[]>('/ml/cluster', {
      params: { limit },
    })
    return data
  },

  // Get anomalies
  async getAnomalies(limit: number = 50) {
    const { data } = await apiClient.get<AnomalyDetail[]>('/ml/anomalies', {
      params: { limit },
    })
    return data
  },
}
