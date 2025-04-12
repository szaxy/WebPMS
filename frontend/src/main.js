import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/authStore'

// 引入自定义样式
import './assets/styles/shot-status.css'
// 引入字体样式
import './assets/styles/fonts.css'
// 引入ElementPlus自定义样式
import './assets/styles/element-plus-custom.css'

// 使用异步IIFE初始化应用
(async () => {
  const app = createApp(App)
  const pinia = createPinia()
  
  // 注册所有Element Plus图标
  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
  
  app.use(pinia)
  app.use(router)
  app.use(ElementPlus, {
    locale: zhCn,
  })
  
  // 初始化auth store
  const authStore = useAuthStore()
  await authStore.init()
  
  app.mount('#app')
})(); 