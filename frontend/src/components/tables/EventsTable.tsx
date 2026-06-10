'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle, Badge, Skeleton } from '@/components/ui'
import { EventRecord } from '@/types'
import { formatDateTime, getSeverityColor } from '@/lib/utils'
import { ChevronRight } from 'lucide-react'

interface EventsTableProps {
  events: EventRecord[]
  isLoading?: boolean
  onRowClick?: (event: EventRecord) => void
}

export function EventsTable({
  events,
  isLoading = false,
  onRowClick,
}: EventsTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Últimos Eventos</CardTitle>
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
      <p className="text-text-secondary">Nenhum evento encontrado</p>
    </div>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle>Últimos Eventos</CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          emptyState
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-purple/10">
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Tipo
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    IP Origem
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Severidade
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-text-secondary">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody>
                {events.map((event) => (
                  <tr
                    key={event.id}
                    className="border-b border-brand-purple/5 hover:bg-brand-purple/5 transition-colors cursor-pointer"
                    onClick={() => onRowClick?.(event)}
                  >
                    <td className="py-3 px-4 text-text-primary font-medium">
                      {event.event_type}
                    </td>
                    <td className="py-3 px-4 text-text-secondary font-mono">
                      {event.source_ip}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant={event.severity as any}>
                        {event.severity.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-text-secondary text-xs">
                      {formatDateTime(event.timestamp)}
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
