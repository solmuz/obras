import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        verde: '#10b981',
        amarillo: '#f59e0b',
        rojo: '#ef4444',
      },
    },
  },
  plugins: [],
} satisfies Config
