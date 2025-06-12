import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0', // Allow external connections (required for Docker)
    port: 5173,
    watch: {
      usePolling: true, // Enable polling for file changes in Docker
    },
    hmr: {
      host: 'localhost', // HMR host for browser connections
    },
  },
})
