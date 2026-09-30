import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // tudo que comeca com /api vai pro Rails, evitando CORS no desenvolvimento
    proxy: {
      '/api': 'http://localhost:3000',
      '/rails': 'http://localhost:3000',
    },
  },
})
