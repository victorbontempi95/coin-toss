import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8000,
    allowedHosts: [
      'ct-frontend-production.up.railway.app',
      '.railway.app', // Allow all railway.app subdomains
      'localhost'
    ]
  }
})