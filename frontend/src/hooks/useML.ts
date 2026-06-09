import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { mlService } from '@/services/ml'
import { NormalizedEvent } from '@/types'

export const useModelStatus = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['model-status'],
    queryFn: () => mlService.getModelStatus(),
    enabled,
    staleTime: 30000,
    retry: 2,
  })
}

export const useTrainModel = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (limit?: number) => mlService.trainModel(limit),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-status'] })
    },
  })
}

export const useScoreEvent = () => {
  return useMutation({
    mutationFn: (event: NormalizedEvent) => mlService.scoreEvent(event),
  })
}

export const useClusterEvents = () => {
  return useQuery({
    queryKey: ['ml-clusters'],
    queryFn: () => mlService.clusterEvents(),
    staleTime: 60000,
    retry: 2,
  })
}

export const useAnomalies = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['anomalies'],
    queryFn: () => mlService.getAnomalies(),
    enabled,
    staleTime: 60000,
    retry: 2,
  })
}
