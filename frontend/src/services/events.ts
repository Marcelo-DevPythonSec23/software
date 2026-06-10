import { apiClient } from './api'
import {
  EventRecord,
  QueryResponse,
  FilterParams,
  UploadResponse,
} from '@/types'

export const eventsService = {
  // Get all events
  async getEvents(params?: FilterParams) {
    const { data } = await apiClient.get<QueryResponse>('/events', {
      params,
    })
    return data
  },

  // Search events by IOC
  async searchByIOC(ioc: string, limit: number = 100) {
    const { data } = await apiClient.get<EventRecord[]>('/events/search', {
      params: { ioc, limit },
    })
    return data
  },

  // Get event count
  async getEventCount() {
    const { data } = await apiClient.get<{ count: number }>('/events/count')
    return data.count
  },

  // Upload file for ingestion
  async uploadFile(filePath: string) {
    const { data } = await apiClient.post<UploadResponse>('/ingest/file', null, {
      params: { path: filePath },
    })
    return data
  },

  // Get events by severity
  async getEventsBySeverity() {
    const response = await this.getEvents({ limit: 500 })
    const grouped = {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    }

    response.items?.forEach((event) => {
      grouped[event.severity as keyof typeof grouped]++
    })

    return grouped
  },
}
