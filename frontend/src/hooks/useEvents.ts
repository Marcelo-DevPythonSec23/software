import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { eventsService } from '@/services/events'
import { FilterParams } from '@/types'

export const useEvents = (params?: FilterParams) => {
  return useQuery({
    queryKey: ['events', params],
    queryFn: () => eventsService.getEvents(params),
    staleTime: 30000,
    retry: 2,
  })
}

export const useSearchIOC = (ioc: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['search-ioc', ioc],
    queryFn: () => eventsService.searchByIOC(ioc),
    enabled: !!ioc && enabled,
    staleTime: 30000,
    retry: 1,
  })
}

export const useEventCount = () => {
  return useQuery({
    queryKey: ['event-count'],
    queryFn: () => eventsService.getEventCount(),
    staleTime: 60000,
    retry: 2,
  })
}

export const useEventsBySeverity = () => {
  return useQuery({
    queryKey: ['events-by-severity'],
    queryFn: () => eventsService.getEventsBySeverity(),
    staleTime: 30000,
    retry: 2,
  })
}

export const useUploadFile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (filePath: string) => eventsService.uploadFile(filePath),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] })
      queryClient.invalidateQueries({ queryKey: ['event-count'] })
    },
  })
}
