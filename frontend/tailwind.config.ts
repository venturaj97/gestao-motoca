import forms from '@tailwindcss/forms'
import type { Config } from 'tailwindcss'

export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{vue,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0e0e10',
        surface: '#0e0e10',
        'surface-container-lowest': '#000000',
        'surface-container-low': '#131315',
        'surface-container': '#19191c',
        'surface-container-high': '#1f1f22',
        'surface-container-highest': '#262528',
        'surface-bright': '#2c2c2f',
        outline: '#767577',
        'outline-variant': '#48474a',
        primary: '#f3ffca',
        'primary-dim': '#beee00',
        'primary-container': '#cafd00',
        secondary: '#ff6e85',
        'secondary-dim': '#e31754',
        'secondary-container': '#bd0042',
        error: '#ff7351',
        'error-container': '#b92902',
        'on-surface': '#f9f5f8',
        'on-surface-variant': '#adaaad',
        'on-primary-fixed': '#3a4a00',
        'on-primary-container': '#4a5e00',
        'on-secondary-container': '#fff6f5',
      },
      fontFamily: {
        headline: ['"Space Grotesk"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        label: ['"Space Grotesk"', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0px',
        lg: '0px',
        xl: '0px',
      },
      boxShadow: {
        tactical: '0 0 30px rgba(202, 253, 0, 0.12)',
      },
    },
  },
  plugins: [forms],
} satisfies Config
