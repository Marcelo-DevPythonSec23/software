'use client'

import React from 'react'
import { Sidebar } from './Sidebar'
import { Toaster } from 'sonner'

export function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      <Sidebar />
      <main className="ml-64 transition-all duration-300">
        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
      <Toaster
        position="bottom-right"
        theme="dark"
        richColors
        closeButton
      />
    </div>
  )
}
