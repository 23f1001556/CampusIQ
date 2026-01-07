import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
        '/auth': 'http://127.0.0.1:5000',
        '/users': 'http://127.0.0.1:5000',
        '/subjects': 'http://127.0.0.1:5000',
        '/chapters': 'http://127.0.0.1:5000',
        '/quiz': 'http://127.0.0.1:5000',
        '/mock': 'http://127.0.0.1:5000',
        '/ai': 'http://127.0.0.1:5000',
        '/admin': 'http://127.0.0.1:5000',
    }
  }
})
