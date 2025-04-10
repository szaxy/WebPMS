import { ref, onUnmounted } from 'vue'

// WebSocket状态常量
const CONNECTING = 0
const OPEN = 1
const CLOSING = 2
const CLOSED = 3

// 获取WebSocket URL，根据环境变量或当前域名
const getWebSocketUrl = () => {
  const apiUrl = import.meta.env.VITE_API_URL || ''
  if (apiUrl) {
    return apiUrl.replace(/^http/, 'ws') + '/ws/'
  }
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}/ws/`
}

export function useWebSocket() {
  // WebSocket实例
  const socket = ref(null)
  // 连接状态
  const isConnected = ref(false)
  // 消息处理函数映射
  const listeners = ref({})
  // 重连次数
  const reconnectCount = ref(0)
  // 最大重连次数
  const MAX_RECONNECT = 5
  // 重连计时器
  let reconnectTimer = null
  
  // 建立WebSocket连接
  const connect = () => {
    if (socket.value && [CONNECTING, OPEN].includes(socket.value.readyState)) {
      return
    }
    
    try {
      const wsUrl = getWebSocketUrl()
      socket.value = new WebSocket(wsUrl)
      
      // 监听连接打开
      socket.value.onopen = () => {
        console.log('WebSocket连接已建立')
        isConnected.value = true
        reconnectCount.value = 0
        
        // 重新订阅之前的频道
        Object.keys(listeners.value).forEach(channel => {
          sendMessage('subscribe', { channel })
        })
      }
      
      // 监听接收消息
      socket.value.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // 处理消息
          if (data.type && data.channel && listeners.value[data.channel]) {
            listeners.value[data.channel](data)
          }
        } catch (e) {
          console.error('解析WebSocket消息失败', e)
        }
      }
      
      // 监听连接关闭
      socket.value.onclose = () => {
        console.log('WebSocket连接已关闭')
        isConnected.value = false
        
        // 尝试重连
        if (reconnectCount.value < MAX_RECONNECT) {
          reconnectCount.value++
          const delay = Math.pow(2, reconnectCount.value) * 1000
          console.log(`${delay}毫秒后尝试重新连接...`)
          
          reconnectTimer = setTimeout(() => {
            connect()
          }, delay)
        }
      }
      
      // 监听错误
      socket.value.onerror = (error) => {
        console.error('WebSocket连接错误', error)
      }
    } catch (e) {
      console.error('创建WebSocket连接失败', e)
    }
  }
  
  // 关闭WebSocket连接
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    
    if (socket.value && [CONNECTING, OPEN].includes(socket.value.readyState)) {
      socket.value.close()
    }
  }
  
  // 发送消息
  const sendMessage = (type, data = {}) => {
    if (socket.value && socket.value.readyState === OPEN) {
      const message = JSON.stringify({
        type,
        ...data
      })
      socket.value.send(message)
      return true
    }
    return false
  }
  
  // 订阅频道
  const subscribe = (channel, callback) => {
    listeners.value[channel] = callback
    
    // 如果已连接，发送订阅消息
    if (isConnected.value) {
      sendMessage('subscribe', { channel })
    }
    
    return () => {
      unsubscribe(channel)
    }
  }
  
  // 取消订阅
  const unsubscribe = (channel) => {
    if (listeners.value[channel]) {
      delete listeners.value[channel]
      
      // 如果已连接，发送取消订阅消息
      if (isConnected.value) {
        sendMessage('unsubscribe', { channel })
      }
    }
  }
  
  // 组件卸载时自动断开连接
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    connect,
    disconnect,
    sendMessage,
    subscribe,
    unsubscribe,
    isConnected
  }
} 