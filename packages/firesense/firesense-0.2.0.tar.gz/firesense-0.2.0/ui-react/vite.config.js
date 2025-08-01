import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 9090,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/analysis_config.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/detection_results.json': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})