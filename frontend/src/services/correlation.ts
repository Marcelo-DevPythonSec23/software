import { apiClient } from './api'
import {
  CorrelationResponse,
  ReusedIOC,
} from '@/types'

export const correlationService = {
  // Get correlation by IP
  async getCorrelationByIP(timeWindow: number = 3600) {
    const { data } = await apiClient.get<CorrelationResponse>(
      '/correlation/ip',
      {
        params: { time_window: timeWindow },
      }
    )
    return data
  },

  // Get reused IOCs
  async getReusedIOCs(minReuse: number = 2) {
    const { data } = await apiClient.get<ReusedIOC[]>('/correlation/reused', {
      params: { min_reuse: minReuse },
    })
    return data
  },

  // Search IOC with context
  async searchIOC(ioc: string) {
    const { data } = await apiClient.get<any>('/events/search', {
      params: { ioc },
    })
    return data
  },
}
