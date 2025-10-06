import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Bundle optimization
    rollupOptions: {
      output: {
        manualChunks: {
          // Core vendor chunks
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
          // Heavy libraries - lazy load when possible
          'chart-vendor': ['recharts'],
          // State management
          'state-vendor': ['zustand'],
        },
      },
    },
    // Optimize chunk size
    chunkSizeWarningLimit: 1000,
    // Minification (using esbuild for better compatibility)
    minify: 'esbuild',
    // Source maps for production debugging
    sourcemap: false, // Disable in production for performance
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@tanstack/react-query',
      'axios',
    ],
  },
  // Server configuration
  server: {
    port: 3000,
    strictPort: true,
    host: true,
  },
  // Preview configuration
  preview: {
    port: 4173,
    strictPort: true,
  },
})
