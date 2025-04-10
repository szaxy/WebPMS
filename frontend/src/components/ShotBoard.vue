<template>
  <div class="shot-board">
    <div class="board-header">
      <h2>镜头状态看板</h2>
      <el-button type="primary" @click="refreshData">刷新数据</el-button>
    </div>
    
    <div class="board-content">
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
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
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
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
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
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
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
              >
                <template #item="{ element }">
                  <shot-card :shot="element" @click="openShotDetails(element)" />
                </template>
              </draggable>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 镜头详情对话框 -->
    <el-dialog v-model="dialogVisible" title="镜头详情" width="70%">
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import draggable from 'vuedraggable'
import ShotCard from './ShotCard.vue'
import ShotDetails from './ShotDetails.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useShotStore } from '../stores/shotStore'
import shotService from '../services/shotService'

const props = defineProps({
  projectId: {
    type: [Number, String],
    required: true
  }
})

// 状态数据
const shotStore = useShotStore()
const loading = ref(true)
const dialogVisible = ref(false)
const selectedShot = ref(null)

// 按状态分组的计算属性
const inProgressShots = computed(() => {
  return shotStore.shots.filter(shot => shot.status === 'in_progress')
})

const reviewShots = computed(() => {
  return shotStore.shots.filter(shot => shot.status === 'review')
})

const approvedShots = computed(() => {
  return shotStore.shots.filter(shot => shot.status === 'approved')
})

const needRevisionShots = computed(() => {
  return shotStore.shots.filter(shot => shot.status === 'need_revision')
})

// 加载镜头数据
const loadShots = async () => {
  loading.value = true
  try {
    await shotStore.fetchShots({ project_id: props.projectId })
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
  const shotId = item.dataset.id
  const shot = shotStore.getShotById(parseInt(shotId))
  
  if (!shot) return
  
  // 根据目标列表确定新状态
  let newStatus = 'in_progress'
  if (to.classList.contains('review')) {
    newStatus = 'review'
  } else if (to.classList.contains('approved')) {
    newStatus = 'approved'
  } else if (to.classList.contains('need-revision')) {
    newStatus = 'need_revision'
  }
  
  // 如果状态未变，不执行更新
  if (shot.status === newStatus) return
  
  try {
    // 乐观更新本地状态
    shotStore.updateShot({ ...shot, status: newStatus })
    
    // 发送API请求更新后端
    await shotService.updateShot(shot.id, { status: newStatus })
    
    ElMessage.success(`镜头 ${shot.shot_code} 状态已更新为 ${newStatus}`)
  } catch (err) {
    // 恢复原状态
    shotStore.updateShot({ ...shot, status: shot.status })
    ElMessage.error('更新状态失败')
    console.error(err)
  }
}

// 打开镜头详情
const openShotDetails = (shot) => {
  selectedShot.value = shot
  dialogVisible.value = true
}

// 更新镜头信息
const updateShot = (updatedShot) => {
  shotStore.updateShot(updatedShot)
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
      shotStore.updateShot(updatedShot)
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

.board-content {
  flex: 1;
  overflow: hidden;
}

.status-column {
  background-color: #f5f7fa;
  border-radius: 4px;
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  color: white;
}

.column-header h3 {
  margin: 0;
  font-size: 16px;
}

.shot-count {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
}

.in-progress {
  background-color: #409eff;
}

.review {
  background-color: #e6a23c;
}

.approved {
  background-color: #67c23a;
}

.need-revision {
  background-color: #f56c6c;
}

.shot-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.drag-area {
  min-height: 100%;
}
</style> 