import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.FRONTEND_PORT || 3000),
    strictPort: false, // 允许自动寻找可用端口
    proxy: {
      '/api': {
        target: `http://backend:${process.env.BACKEND_PORT || 8000}`,
        changeOrigin: true,
      },
      '/media': {
        target: `http://backend:${process.env.BACKEND_PORT || 8000}`,
        changeOrigin: true,
      },
      '/ws': {
        target: `ws://backend:${process.env.BACKEND_PORT || 8000}`,
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
}) 