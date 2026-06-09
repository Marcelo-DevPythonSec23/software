import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

export function formatTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function formatDateTime(date: string | Date): string {
  return `${formatDate(date)} ${formatTime(date)}`
}

export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-status-critical'
    case 'high':
      return 'text-orange-500'
    case 'medium':
      return 'text-status-warning'
    case 'low':
      return 'text-status-success'
    default:
      return 'text-text-secondary'
  }
}

export function getSeverityBgColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-status-critical/20'
    case 'high':
      return 'bg-orange-500/20'
    case 'medium':
      return 'bg-status-warning/20'
    case 'low':
      return 'bg-status-success/20'
    default:
      return 'bg-bg-tertiary'
  }
}

export function formatNumber(num: number): string {
  return num.toLocaleString('pt-BR')
}

export function truncate(str: string, length: number): string {
  return str.length > length ? str.substring(0, length) + '...' : str
}
