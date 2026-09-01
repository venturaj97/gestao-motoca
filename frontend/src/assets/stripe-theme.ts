import type { Appearance } from '@stripe/stripe-js'

export const stripeCustomAppearance: Appearance = {
  theme: 'night',
  variables: {
    colorPrimary: '#f59e0b',
    colorBackground: '#0f172a',
    colorText: '#f8fafc',
    colorDanger: '#ef4444',
    colorTextSecondary: '#94a3b8',
    colorTextPlaceholder: '#64748b',
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    spacingUnit: '4px',
    borderRadius: '12px',
  },
  rules: {
    '.Input': {
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      boxShadow: 'none',
      transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
    },
    '.Input:focus': {
      borderColor: '#f59e0b',
      boxShadow: '0 0 0 2px rgba(245, 158, 11, 0.25)',
    },
    '.Label': {
      color: '#cbd5e1',
      fontWeight: '600',
      fontSize: '0.85rem',
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
    },
    '.Tab': {
      backgroundColor: '#1e293b',
      borderColor: '#334155',
      color: '#94a3b8',
    },
    '.Tab:hover': {
      color: '#f8fafc',
      borderColor: '#475569',
    },
    '.Tab--selected': {
      backgroundColor: 'rgba(245, 158, 11, 0.15)',
      borderColor: '#f59e0b',
      color: '#fbbf24',
    },
    '.Block': {
      backgroundColor: '#0f172a',
      borderColor: '#334155',
    },
  },
}
