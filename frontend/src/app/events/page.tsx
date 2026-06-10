'use client'

import React, { useState } from 'react'
import { MainLayout } from '@/components/layouts/MainLayout'
import { Card, CardContent, CardHeader, CardTitle, Button, Input } from '@/components/ui'
import { EventsTable } from '@/components/tables/EventsTable'
import { CustomBarChart } from '@/components/charts/CustomBarChart'
import { useEvents, useSearchIOC } from '@/hooks/useEvents'
import { Search, FileUp } from 'lucide-react'

export default function EventsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  // Debounce search
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm)
    }, 500)

    return () => clearTimeout(timer)
  }, [searchTerm])

  const { data: events, isLoading: eventsLoading } = useEvents({ limit: 100 })
  const { data: searchResults, isLoading: searchLoading } = useSearchIOC(
    debouncedSearch,
    debouncedSearch.length > 0
  )

  const displayEvents = debouncedSearch && searchResults
    ? searchResults
    : events?.items || []

  // Generate event types data
  const eventTypesData = React.useMemo(() => {
    const grouped: Record<string, number> = {}
    events?.items?.forEach((event) => {
      grouped[event.event_type] = (grouped[event.event_type] || 0) + 1
    })
    return Object.entries(grouped)
      .map(([name, value]) => ({ name, value }))
      .slice(0, 10)
  }, [events])

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Eventos</h1>
            <p className="text-text-secondary mt-2">
              Visualize e analise todos os eventos de segurança capturados
            </p>
          </div>
          <Button variant="default" className="flex items-center gap-2">
            <FileUp className="w-4 h-4" />
            Upload
          </Button>
        </div>

        {/* Filters and Search */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Filtros</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-text-secondary" />
                <Input
                  placeholder="Buscar por IP, tipo de evento..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Charts */}
        <CustomBarChart
          data={eventTypesData}
          title="Top 10 Tipos de Eventos"
          color="#7C3AED"
          isLoading={eventsLoading}
        />

        {/* Events Table */}
        <EventsTable
          events={displayEvents}
          isLoading={searchLoading || eventsLoading}
        />
      </div>
    </MainLayout>
  )
}
