'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  Network,
  Zap,
  Shield,
  BarChart3,
  Settings,
  ChevronDown,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavItem {
  title: string
  href: string
  icon: React.ReactNode
  disabled?: boolean
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/',
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    title: 'Eventos',
    href: '/events',
    icon: <Shield className="w-5 h-5" />,
  },
  {
    title: 'Correlação',
    href: '/correlation',
    icon: <Network className="w-5 h-5" />,
  },
  {
    title: 'Machine Learning',
    href: '/ml',
    icon: <Zap className="w-5 h-5" />,
  },
  {
    title: 'Relatórios',
    href: '/reports',
    icon: <BarChart3 className="w-5 h-5" />,
  },
  {
    title: 'Configurações',
    href: '/settings',
    icon: <Settings className="w-5 h-5" />,
    disabled: true,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [isCollapsed, setIsCollapsed] = React.useState(false)

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-gradient-dark border-r border-brand-purple/10 transition-all duration-300',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-6 border-b border-brand-purple/10">
        <div className={cn('flex items-center gap-2', isCollapsed && 'justify-center w-full')}>
          <div className="w-8 h-8 rounded-lg bg-gradient-purple flex items-center justify-center shadow-purple-glow">
            <Shield className="w-5 h-5 text-white" />
          </div>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-sm font-bold text-text-primary">CTI</span>
              <span className="text-xs text-text-secondary">Forensic</span>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-6 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200',
              'hover:bg-brand-purple/10 text-text-secondary hover:text-brand-purple-light',
              pathname === item.href && 'bg-brand-purple/20 text-brand-purple-light shadow-purple-glow-sm',
              item.disabled && 'opacity-50 cursor-not-allowed pointer-events-none'
            )}
            title={isCollapsed ? item.title : ''}
          >
            {item.icon}
            {!isCollapsed && (
              <>
                <span className="text-sm font-medium flex-1">{item.title}</span>
                {item.disabled && <span className="text-xs text-text-secondary">Soon</span>}
              </>
            )}
          </Link>
        ))}
      </nav>

      {/* Collapse Button */}
      <div className="border-t border-brand-purple/10 p-3">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-center px-3 py-2 rounded-lg hover:bg-brand-purple/10 transition-colors"
          title={isCollapsed ? 'Expand' : 'Collapse'}
        >
          <ChevronDown
            className={cn(
              'w-5 h-5 text-text-secondary transition-transform',
              isCollapsed && 'rotate-90'
            )}
          />
        </button>
      </div>
    </aside>
  )
}
