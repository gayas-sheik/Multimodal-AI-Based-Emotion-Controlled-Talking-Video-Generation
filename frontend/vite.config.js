import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      // The browser smoke test owns these profile databases on Windows.
      // Excluding them prevents Vite's file watcher from crashing.
      ignored: ['**/.edge-smoke-profile/**', '**/.edge-smoke-profile-*/**'],
    },
  },
})
