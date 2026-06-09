import { useQuery } from '@tanstack/react-query'
import { correlationService } from '@/services/correlation'

export const useCorrelation = (timeWindow: number = 3600, enabled: boolean = true) => {
  return useQuery({
    queryKey: ['correlation', timeWindow],
    queryFn: () => correlationService.getCorrelationByIP(timeWindow),
    enabled,
    staleTime: 60000,
    retry: 2,
  })
}

export const useReusedIOCs = (enabled: boolean = true) => {
  return useQuery({
    queryKey: ['reused-iocs'],
    queryFn: () => correlationService.getReusedIOCs(),
    enabled,
    staleTime: 60000,
    retry: 2,
  })
}

export const useSearchIOCDetail = (ioc: string, enabled: boolean = false) => {
  return useQuery({
    queryKey: ['search-ioc-detail', ioc],
    queryFn: () => correlationService.searchIOC(ioc),
    enabled: !!ioc && enabled,
    staleTime: 30000,
    retry: 1,
  })
}
