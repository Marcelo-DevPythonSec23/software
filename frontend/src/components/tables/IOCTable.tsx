'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, Badge, Skeleton } from '@/components/ui'
import { ReusedIOC } from '@/types'
import { formatDateTime, formatNumber } from '@/lib/utils'

interface IOCTableProps {
  iocs: ReusedIOC[]
  isLoading?: boolean
  onIOCClick?: (ioc: string) => void
}

export function IOCTable({
  iocs,
  isLoading = false,
  onIOCClick,
}: IOCTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>IOCs Reutilizados</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  const emptyState = (
    <div className="flex flex-col items-center justify-center py-8">
      <p className="text-text-secondary">Nenhum IOC encontrado</p>
    </div>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>IOCs Reutilizados</CardTitle>
      </CardHeader>
      <CardContent>
        {iocs.length === 0 ? (
          emptyState
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-purple/10">
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    IOC (IP)
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Ocorrências
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Severidade Máx.
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Visto
                  </th>
                </tr>
              </thead>
              <tbody>
                {iocs.slice(0, 10).map((ioc) => (
                  <tr
                    key={ioc.ioc}
                    className="border-b border-brand-purple/5 hover:bg-brand-purple/5 transition-colors cursor-pointer"
                    onClick={() => onIOCClick?.(ioc.ioc)}
                  >
                    <td className="py-3 px-4 text-text-primary font-mono">
                      {ioc.ioc}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-semibold">
                      {formatNumber(ioc.occurrence_count)}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={ioc.severity_max as any}>
                        {ioc.severity_max.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-text-secondary text-xs">
                      {formatDateTime(ioc.last_seen)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
