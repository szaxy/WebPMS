<template>
  <div class="shot-board">
    <div class="board-header">
      <h2>镜头状态看板</h2>
      <div class="board-controls">
        <el-select v-model="filterOptions.status" placeholder="状态筛选" clearable>
          <el-option label="全部状态" value=""></el-option>
          <el-option label="制作中" value="in_progress"></el-option>
          <el-option label="审核中" value="review"></el-option>
          <el-option label="已通过" value="approved"></el-option>
          <el-option label="需修改" value="need_revision"></el-option>
        </el-select>
        
        <el-input
          v-model="filterOptions.search"
          placeholder="搜索镜头编号"
          prefix-icon="Search"
          clearable
          @clear="refreshData"
        />
        
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon> 刷新数据
        </el-button>
      </div>
    </div>
    
    <div class="board-content" v-loading="loading">
      <el-row :gutter="20">
        <!-- 制作中 -->
        <el-col :span="6">
          <div class="status-column">
            <div class="column-header in-progress">
              <h3>制作中</h3>
              <span class="shot-count">{{ inProgressShots.length }}</span>
            </div>
            <div class="shot-list">
              <draggable 
                v-model="inProgressShots" 
                group="shots"
                @end="onDragEnd"
                item-key="id"
                class="drag-area"
                :animation="150"
                ghost-class="ghost-shot"
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
                </template>
                <template #header>
                  <div class="shot-list-header">
                    <el-icon><DArrowDown /></el-icon> 拖拽镜头卡片以更新状态
                  </div>
                </template>
                <template #footer v-if="inProgressShots.length === 0">
                  <div class="empty-placeholder">
                    <el-empty description="暂无制作中的镜头" />
                  </div>
                </template>
              </draggable>
            </div>
          </div>
        </el-col>
        
        <!-- 审核中 -->
        <el-col :span="6">
          <div class="status-column">
            <div class="column-header review">
              <h3>审核中</h3>
              <span class="shot-count">{{ reviewShots.length }}</span>
            </div>
            <div class="shot-list">
              <draggable 
                v-model="reviewShots" 
                group="shots"
                @end="onDragEnd"
                item-key="id"
                class="drag-area"
                :animation="150"
                ghost-class="ghost-shot"
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
                </template>
                <template #footer v-if="reviewShots.length === 0">
                  <div class="empty-placeholder">
                    <el-empty description="暂无审核中的镜头" />
                  </div>
                </template>
              </draggable>
            </div>
          </div>
        </el-col>
        
        <!-- 已通过 -->
        <el-col :span="6">
          <div class="status-column">
            <div class="column-header approved">
              <h3>已通过</h3>
              <span class="shot-count">{{ approvedShots.length }}</span>
            </div>
            <div class="shot-list">
              <draggable 
                v-model="approvedShots" 
                group="shots"
                @end="onDragEnd"
                item-key="id"
                class="drag-area"
                :animation="150"
                ghost-class="ghost-shot"
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
                </template>
                <template #footer v-if="approvedShots.length === 0">
                  <div class="empty-placeholder">
                    <el-empty description="暂无已通过的镜头" />
                  </div>
                </template>
              </draggable>
            </div>
          </div>
        </el-col>
        
        <!-- 需修改 -->
        <el-col :span="6">
          <div class="status-column">
            <div class="column-header need-revision">
              <h3>需修改</h3>
              <span class="shot-count">{{ needRevisionShots.length }}</span>
            </div>
            <div class="shot-list">
              <draggable 
                v-model="needRevisionShots" 
                group="shots"
                @end="onDragEnd"
                item-key="id"
                class="drag-area"
                :animation="150"
                ghost-class="ghost-shot"
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
                </template>
                <template #footer v-if="needRevisionShots.length === 0">
                  <div class="empty-placeholder">
                    <el-empty description="暂无需修改的镜头" />
                  </div>
                </template>
              </draggable>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 镜头详情对话框 -->
    <el-dialog v-model="dialogVisible" title="镜头详情" width="70%" destroy-on-close>
      <shot-details 
        v-if="selectedShot" 
        :shot="selectedShot" 
        @update:shot="updateShot"
        @close="dialogVisible = false" 
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, DArrowDown } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import ShotCard from './ShotCard.vue'
import ShotDetails from './ShotDetails.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useShotStore } from '../stores/shotStore'

const props = defineProps({
  projectId: {
    type: [Number, String],
    required: true
  }
})

// 状态数据
const shotStore = useShotStore()
const loading = ref(false)
const dialogVisible = ref(false)
const selectedShot = ref(null)
const filterOptions = ref({
  status: '',
  search: '',
})

// 按状态分组的计算属性
const filteredShots = computed(() => {
  let shots = shotStore.shots || []
  
  // 状态筛选
  if (filterOptions.value.status) {
    shots = shots.filter(shot => shot.status === filterOptions.value.status)
  }
  
  // 搜索筛选
  if (filterOptions.value.search) {
    const searchTerm = filterOptions.value.search.toLowerCase()
    shots = shots.filter(shot => 
      (shot.shot_code && shot.shot_code.toLowerCase().includes(searchTerm)) || 
      (shot.description && shot.description.toLowerCase().includes(searchTerm))
    )
  }
  
  return shots
})

const inProgressShots = computed(() => {
  return filteredShots.value.filter(shot => shot.status === 'in_progress')
})

const reviewShots = computed(() => {
  return filteredShots.value.filter(shot => shot.status === 'review')
})

const approvedShots = computed(() => {
  return filteredShots.value.filter(shot => shot.status === 'approved')
})

const needRevisionShots = computed(() => {
  return filteredShots.value.filter(shot => shot.status === 'need_revision')
})

// 监听筛选条件变化
watch(filterOptions, () => {
  // 只在搜索条件变化且搜索框内容不为空时自动刷新
  if (filterOptions.value.search && filterOptions.value.search.length > 2) {
    refreshData()
  }
}, { deep: true })

// 加载镜头数据
const loadShots = async () => {
  loading.value = true
  try {
    const params = { project: props.projectId }
    
    if (filterOptions.value.status) {
      params.status = filterOptions.value.status
    }
    
    if (filterOptions.value.search) {
      params.search = filterOptions.value.search
    }
    
    await shotStore.fetchShots(params)
    
  } catch (err) {
    ElMessage.error('加载镜头数据失败')
    console.error(err)
  } finally {
    loading.value = false
  }
}

// 刷新数据
const refreshData = () => {
  loadShots()
}

// 处理拖拽结束事件
const onDragEnd = async (evt) => {
  const { item, to } = evt
  
  if (!item || !to) return
  
  const shotId = parseInt(item.getAttribute('data-id'))
  if (!shotId) return
  
  const shot = shotStore.shots.find(s => s.id === shotId)
  if (!shot) return
  
  // 根据目标列表确定新状态
  let newStatus = ''
  
  if (to.closest('.in-progress')) {
    newStatus = 'in_progress'
  } else if (to.closest('.review')) {
    newStatus = 'review'
  } else if (to.closest('.approved')) {
    newStatus = 'approved'
  } else if (to.closest('.need-revision')) {
    newStatus = 'need_revision'
  }
  
  // 如果状态未变，不执行更新
  if (!newStatus || shot.status === newStatus) return
  
  try {
    // 更新状态
    await shotStore.updateShotStatus(shotId, newStatus)
    
    ElMessage({
      message: `镜头 ${shot.shot_code} 状态已更新为 ${getStatusText(newStatus)}`,
      type: 'success'
    })
  } catch (err) {
    ElMessage.error('更新状态失败')
    console.error(err)
    
    // 刷新以恢复正确状态
    refreshData()
  }
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

// 打开镜头详情
const openShotDetails = (shot) => {
  selectedShot.value = shot
  dialogVisible.value = true
}

// 更新镜头信息
const updateShot = async (updatedShot) => {
  try {
    await shotStore.updateShot(updatedShot.id, updatedShot)
    ElMessage.success('镜头信息已更新')
  } catch (err) {
    ElMessage.error('更新镜头失败')
    console.error(err)
  }
}

// WebSocket实时更新
const { connect, disconnect, subscribe } = useWebSocket()

onMounted(() => {
  loadShots()
  
  // 连接WebSocket
  connect()
  
  // 订阅项目更新
  subscribe(`project.${props.projectId}`, (message) => {
    if (message.type === 'shot_update') {
      const updatedShot = message.data
      
      // 更新状态存储
      const index = shotStore.shots.findIndex(s => s.id === updatedShot.id)
      if (index > -1) {
        shotStore.shots[index] = updatedShot
      } else {
        shotStore.shots.push(updatedShot)
      }
      
      // 更新详情对话框中的数据
      if (selectedShot.value && selectedShot.value.id === updatedShot.id) {
        selectedShot.value = updatedShot
      }
      
      ElMessage({
        message: `镜头 ${updatedShot.shot_code} 已被更新`,
        type: 'info'
      })
    } else if (message.type === 'shot_create') {
      const newShot = message.data
      shotStore.shots.push(newShot)
      
      ElMessage({
        message: `新镜头 ${newShot.shot_code} 已添加`,
        type: 'success'
      })
    } else if (message.type === 'shot_delete') {
      const deletedShotId = message.data.id
      const index = shotStore.shots.findIndex(s => s.id === deletedShotId)
      if (index > -1) {
        const shotCode = shotStore.shots[index].shot_code
        shotStore.shots.splice(index, 1)
        
        ElMessage({
          message: `镜头 ${shotCode} 已被删除`,
          type: 'warning'
        })
      }
    }
  })
})

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.shot-board {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.board-controls {
  display: flex;
  gap: 10px;
}

.board-content {
  flex: 1;
  overflow: hidden;
}

.status-column {
  background-color: #f9f9f9;
  border-radius: 4px;
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}

.column-header h3 {
  margin: 0;
  font-size: 16px;
}

.column-header.in-progress {
  background-color: #e6f7ff;
  color: #1890ff;
}

.column-header.review {
  background-color: #fff7e6;
  color: #fa8c16;
}

.column-header.approved {
  background-color: #f6ffed;
  color: #52c41a;
}

.column-header.need-revision {
  background-color: #fff1f0;
  color: #f5222d;
}

.shot-count {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.shot-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.drag-area {
  min-height: 100%;
}

.ghost-shot {
  opacity: 0.5;
  background: #c8ebfb;
}

.shot-list-header {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
  text-align: center;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}
</style> 