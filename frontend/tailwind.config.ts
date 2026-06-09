import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Background
        'bg-primary': '#0A0A0A',
        'bg-secondary': '#111827',
        'bg-tertiary': '#1F2937',
        
        // Brand
        'brand-purple': '#7C3AED',
        'brand-purple-light': '#8B5CF6',
        'brand-purple-dark': '#6D28D9',
        
        // Status
        'status-success': '#10B981',
        'status-warning': '#F59E0B',
        'status-critical': '#EF4444',
        'status-info': '#3B82F6',
        
        // Text
        'text-primary': '#F8FAFC',
        'text-secondary': '#94A3B8',
      },
      fontFamily: {
        sans: ['Inter', ...defaultTheme.fontFamily.sans],
      },
      boxShadow: {
        'purple-glow': '0 0 20px rgba(124, 58, 237, 0.3)',
        'purple-glow-sm': '0 0 10px rgba(124, 58, 237, 0.2)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.1)',
      },
      backgroundImage: {
        'gradient-purple': 'linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%)',
        'gradient-dark': 'linear-gradient(135deg, #0A0A0A 0%, #111827 100%)',
      },
      backdropBlur: {
        'xl': '16px',
      },
    },
  },
  plugins: [],
}
export default config
