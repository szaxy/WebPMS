import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.FRONTEND_PORT || 9527),
    strictPort: false, // 允许自动寻找可用端口
    proxy: {
      '/api': {
        target: `http://localhost:${process.env.BACKEND_PORT || 9803}`,
        changeOrigin: true,
      },
      '/media': {
        target: `http://localhost:${process.env.BACKEND_PORT || 9803}`,
        changeOrigin: true,
      },
      '/ws': {
        target: `ws://localhost:${process.env.BACKEND_PORT || 9803}`,
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