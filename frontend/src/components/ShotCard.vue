<template>
  <div class="shot-card" :data-id="shot.id" @click="$emit('click', shot)">
    <div class="shot-header">
      <span class="shot-code">{{ shot.shot_code }}</span>
      <el-tag size="small" :type="getStatusType(shot.status)">
        {{ getStatusText(shot.status) }}
      </el-tag>
    </div>
    
    <div class="shot-info">
      <div class="info-item" v-if="shot.deadline">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDate(shot.deadline) }}</span>
      </div>
      
      <div class="info-item" v-if="shot.duration_frame">
        <el-icon><Timer /></el-icon>
        <span>{{ shot.duration_frame }} 帧</span>
      </div>
    </div>
    
    <div class="shot-footer">
      <div class="comment-count" v-if="shot.comment_count">
        <el-icon><ChatDotRound /></el-icon>
        <span>{{ shot.comment_count }}</span>
      </div>
      
      <div class="updated-time">
        <span>{{ formatTime(shot.updated_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Calendar, Timer, ChatDotRound } from '@element-plus/icons-vue'
import { format, formatDistance } from 'date-fns'
import { zhCN } from 'date-fns/locale'

const props = defineProps({
  shot: {
    type: Object,
    required: true
  }
})

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    'in_progress': '',
    'review': 'warning',
    'approved': 'success',
    'need_revision': 'danger'
  }
  return typeMap[status] || ''
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    'in_progress': '制作中',
    'review': '审核中',
    'approved': '已通过',
    'need_revision': '需修改'
  }
  return textMap[status] || '未知'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return format(date, 'MM-dd')
  } catch (e) {
    return dateString
  }
}

// 格式化时间
const formatTime = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return formatDistance(date, new Date(), { 
      addSuffix: true,
      locale: zhCN
    })
  } catch (e) {
    return dateString
  }
}
</script>

<style scoped>
.shot-card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.shot-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
  transform: translateY(-2px);
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.shot-code {
  font-weight: bold;
  font-size: 14px;
}

.shot-info {
  margin-bottom: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.info-item .el-icon {
  margin-right: 4px;
}

.shot-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.comment-count {
  display: flex;
  align-items: center;
}

.comment-count .el-icon {
  margin-right: 2px;
}

.updated-time {
  font-style: italic;
}
</style> 