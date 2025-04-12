<template>
  <div class="shot-details">
    <!-- 头部 -->
    <div class="shot-details-header">
      <h2 class="shot-title">{{ shot.shot_code }}</h2>
      <el-button type="text" @click="closeDetails">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <!-- 内容区域 -->
    <el-scrollbar height="calc(100vh - 60px)">
      <div class="shot-details-content">
        <!-- 常规信息 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <div class="header-actions">
                <el-button v-if="canUpdateStatus" type="success" size="small" @click="statusDialogVisible = true">
                  <el-icon><RefreshRight /></el-icon> 更新状态
                </el-button>
                <el-button v-if="canEdit" type="primary" size="small" plain @click="editShotInfo">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
              </div>
            </div>
          </template>
          <div class="shot-info">
            <!-- 第一行：部门-制作者、推进阶段、制作状态 -->
            <div class="info-row">
              <div class="info-item">
                <div class="info-label">部门-制作者：</div>
                <div class="info-value">{{ shot.department_display }}-{{ shot.artist_name || '未分配' }}</div>
              </div>
              <div class="info-item">
                <div class="info-label">推进阶段：</div>
                <div class="info-value">
                  <el-tag :type="getStageTagType(shot.prom_stage)">
                    {{ shot.prom_stage_display }}
                  </el-tag>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">制作状态：</div>
                <div class="info-value">
                  <el-tag :type="getStatusTagType(shot.status)">
                    {{ shot.status_display }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <!-- 第二行：帧数、截止日期、更新日期 -->
            <div class="info-row">
              <div class="info-item">
                <div class="info-label">帧数：</div>
                <div class="info-value">
                  {{ shot.duration_frame }} <span class="frame-rate">@{{ shot.framepersecond }}</span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">截止日期：</div>
                <div class="info-value">
                  <span :class="getDeadlineClass(shot)">
                    {{ formatDate(shot.deadline) }}
                  </span>
                </div>
              </div>
              <div class="info-item">
                <div class="info-label">更新时间：</div>
                <div class="info-value">{{ formatDateTime(shot.updated_at) }}</div>
              </div>
            </div>
            
            <!-- 描述信息 -->
            <div class="info-description">
              <div class="info-label">描述：</div>
              <div class="info-value description">{{ shot.description || '无描述' }}</div>
            </div>
          </div>
        </el-card>

        <!-- 镜头反馈 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>镜头反馈</span>
              <el-button v-if="canAddComment" type="primary" size="small" plain @click="showAddComment = true">
                <el-icon><Plus /></el-icon> 添加反馈
              </el-button>
            </div>
          </template>
          
          <div v-if="commentsLoading" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="comments.length === 0" class="empty-placeholder">
            <el-empty description="暂无反馈" />
          </div>
          
          <div v-else class="comment-list">
            <div v-for="comment in comments" :key="comment.id" class="comment-item">
              <div class="comment-header">
                <div class="comment-user">{{ comment.user_name }}</div>
                <div class="comment-time">{{ formatDateTime(comment.timestamp) }}</div>
              </div>
              <div class="comment-content">{{ comment.content }}</div>
              <div v-if="comment.is_resolved" class="comment-status">
                <el-tag size="small" type="success">已解决</el-tag>
              </div>
              <div v-if="canResolveComment(comment)" class="comment-actions">
                <el-button v-if="!comment.is_resolved" type="text" size="small" @click="resolveComment(comment.id)">
                  标记为已解决
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 添加反馈对话框 -->
          <el-dialog
            v-model="showAddComment"
            title="添加反馈"
            width="500px"
            :close-on-click-modal="false"
          >
            <el-form ref="commentForm" :model="commentForm" :rules="commentRules">
              <el-form-item prop="content" label="反馈内容">
                <el-input
                  v-model="commentForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入反馈内容"
                />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showAddComment = false">取消</el-button>
              <el-button 
                type="primary" 
                :loading="commentSubmitting"
                @click="submitComment"
              >
                提交
              </el-button>
            </template>
          </el-dialog>
        </el-card>

        <!-- 镜头备注 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>镜头备注</span>
              <el-button type="primary" size="small" plain @click="showAddNote = true">
                <el-icon><Plus /></el-icon> 添加备注
              </el-button>
            </div>
          </template>
          
          <div v-if="notesLoading" class="loading-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="notes.length === 0" class="empty-placeholder">
            <el-empty description="暂无备注" />
          </div>
          
          <div v-else class="note-list">
            <div v-for="note in notes" :key="note.id" class="note-item" :class="{'important-note': note.is_important}">
              <div class="note-header">
                <div class="note-user">{{ note.user_name }}</div>
                <div class="note-time">{{ formatDateTime(note.created_at) }}</div>
              </div>
              <div class="note-content">
                <el-tag v-if="note.is_important" type="danger" size="small" class="important-tag">重要提示</el-tag>
                {{ note.content }}
              </div>
              <div v-if="canDeleteNote(note)" class="note-actions">
                <el-button type="text" size="small" @click="deleteNote(note.id)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 添加备注对话框 -->
          <el-dialog
            v-model="showAddNote"
            title="添加备注"
            width="500px"
            :close-on-click-modal="false"
          >
            <el-form ref="noteForm" :model="noteForm" :rules="noteRules">
              <el-form-item prop="content" label="备注内容">
                <el-input
                  v-model="noteForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入备注内容"
                />
              </el-form-item>
              <el-form-item>
                <el-checkbox v-model="noteForm.is_important">
                  标记为重要提示 <span class="important-hint">(提交状态变更时将提示确认)</span>
                </el-checkbox>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showAddNote = false">取消</el-button>
              <el-button 
                type="primary" 
                :loading="noteSubmitting"
                @click="submitNote"
              >
                提交
              </el-button>
            </template>
          </el-dialog>
        </el-card>
      </div>
    </el-scrollbar>

    <!-- 状态更新对话框 -->
    <el-dialog
      v-model="statusDialogVisible"
      title="更新镜头状态"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="status-update-dialog">
        <el-form label-position="top">
          <el-form-item label="当前状态">
            <el-tag :type="getStatusTagType(shot.status)">
              {{ shot.status_display }}
            </el-tag>
          </el-form-item>
          <el-form-item label="选择新状态">
            <el-select 
              v-model="newStatus" 
              placeholder="选择新状态" 
              class="status-select-full"
              :disabled="statusUpdating"
            >
              <el-option label="等待开始" value="waiting" />
              <el-option label="正在制作" value="in_progress" />
              <el-option label="提交内审" value="submit_review" />
              <el-option label="正在修改" value="revising" />
              <el-option label="内审通过" value="internal_approved" />
              <el-option label="客户审核" value="client_review" />
              <el-option label="客户退回" value="client_rejected" />
              <el-option label="客户通过" value="client_approved" />
              <el-option label="客户返修" value="client_revision" />
              <el-option label="暂停制作" value="suspended" />
              <el-option label="已完结" value="completed" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="statusUpdating"
          :disabled="!newStatus || newStatus === shot.status"
          @click="updateShotStatus"
        >
          更新状态
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, Edit, Plus, RefreshRight } from '@element-plus/icons-vue'
import { useShotStore } from '@/stores/shotStore'
import { useAuthStore } from '@/stores/authStore'
import shotService from '@/services/shotService'
import { formatDate, formatDateTime, getDeadlineClass, getSubmitDateClass } from '@/utils/dateUtils'
import { getStatusTagType, getStageTagType } from '@/utils/statusUtils'

// Props
const props = defineProps({
  shot: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['update', 'close'])

// Store
const shotStore = useShotStore()
const authStore = useAuthStore()

// 数据状态
const comments = ref([])
const notes = ref([])
const commentsLoading = ref(false)
const notesLoading = ref(false)
const commentSubmitting = ref(false)
const noteSubmitting = ref(false)
const statusUpdating = ref(false)
const showAddComment = ref(false)
const showAddNote = ref(false)
const newStatus = ref('')
const statusDialogVisible = ref(false)

// 表单
const commentForm = ref({
  content: ''
})

const noteForm = ref({
  content: '',
  is_important: false
})

// 表单验证规则
const commentRules = {
  content: [
    { required: true, message: '请输入反馈内容', trigger: 'blur' },
    { min: 1, max: 500, message: '长度在1到500个字符之间', trigger: 'blur' }
  ]
}

const noteRules = {
  content: [
    { required: true, message: '请输入备注内容', trigger: 'blur' },
    { min: 1, max: 500, message: '长度在1到500个字符之间', trigger: 'blur' }
  ]
}

// 权限控制
const canEdit = computed(() => {
  return authStore.isAdmin || authStore.isManager
})

const canAddComment = computed(() => {
  return authStore.isAdmin || authStore.isManager
})

const canUpdateStatus = computed(() => {
  const isArtist = props.shot.artist === authStore.user?.id
  return authStore.isAdmin || authStore.isManager || isArtist
})

const canResolveComment = (comment) => {
  return authStore.isAdmin || authStore.isManager || comment.user === authStore.user?.id
}

const canDeleteNote = (note) => {
  return authStore.isAdmin || authStore.isManager || note.user === authStore.user?.id
}

// 加载镜头反馈
const loadComments = async () => {
  commentsLoading.value = true
  try {
    const response = await shotService.getShotComments(props.shot.id)
    comments.value = response.data
  } catch (error) {
    console.error('加载镜头反馈失败', error)
    ElMessage.error('加载镜头反馈失败')
  } finally {
    commentsLoading.value = false
  }
}

// 加载镜头备注
const loadNotes = async () => {
  notesLoading.value = true
  try {
    const response = await shotService.getShotNotes(props.shot.id)
    notes.value = response.data
  } catch (error) {
    console.error('加载镜头备注失败', error)
    ElMessage.error('加载镜头备注失败')
  } finally {
    notesLoading.value = false
  }
}

// 提交反馈
const submitComment = async () => {
  // 表单验证
  try {
    commentSubmitting.value = true
    
    const data = {
      content: commentForm.value.content
    }
    
    await shotService.addShotComment(props.shot.id, data)
    
    // 清空表单
    commentForm.value.content = ''
    showAddComment.value = false
    
    // 重新加载反馈
    await loadComments()
    
    ElMessage.success('反馈添加成功')
  } catch (error) {
    console.error('添加反馈失败', error)
    ElMessage.error('添加反馈失败')
  } finally {
    commentSubmitting.value = false
  }
}

// 解决反馈
const resolveComment = async (commentId) => {
  try {
    await shotService.updateComment(commentId, { is_resolved: true })
    
    // 更新本地状态
    const index = comments.value.findIndex(c => c.id === commentId)
    if (index !== -1) {
      comments.value[index].is_resolved = true
    }
    
    ElMessage.success('已将反馈标记为已解决')
  } catch (error) {
    console.error('更新反馈状态失败', error)
    ElMessage.error('更新反馈状态失败')
  }
}

// 提交备注
const submitNote = async () => {
  try {
    noteSubmitting.value = true
    
    const data = {
      content: noteForm.value.content,
      is_important: noteForm.value.is_important
    }
    
    await shotService.addShotNote(props.shot.id, data)
    
    // 清空表单
    noteForm.value.content = ''
    noteForm.value.is_important = false
    showAddNote.value = false
    
    // 重新加载备注
    await loadNotes()
    
    // 可能需要刷新镜头数据，更新指示器
    const updatedShot = await shotStore.fetchShot(props.shot.id)
    emit('update', updatedShot)
    
    ElMessage.success('备注添加成功')
  } catch (error) {
    console.error('添加备注失败', error)
    ElMessage.error('添加备注失败')
  } finally {
    noteSubmitting.value = false
  }
}

// 删除备注
const deleteNote = async (noteId) => {
  try {
    await ElMessageBox.confirm('确定要删除此备注吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await shotService.deleteShotNote(noteId)
    
    // 更新本地状态
    notes.value = notes.value.filter(n => n.id !== noteId)
    
    // 可能需要刷新镜头数据，更新指示器
    const updatedShot = await shotStore.fetchShot(props.shot.id)
    emit('update', updatedShot)
    
    ElMessage.success('备注删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除备注失败', error)
      ElMessage.error('删除备注失败')
    }
  }
}

// 编辑镜头信息
const editShotInfo = () => {
  // TODO: 实现编辑镜头信息的功能
  ElMessage.info('编辑镜头功能开发中...')
}

// 更新镜头状态
const updateShotStatus = async () => {
  try {
    statusUpdating.value = true
    
    // 如果状态变为提交内审且有重要备注，需要二次确认
    if (newStatus.value === 'submit_review' && props.shot.has_important_notes) {
      try {
        await ElMessageBox.confirm(
          '该镜头有重要备注提示，请确认是否继续提交？', 
          '重要提示', 
          {
            confirmButtonText: '确认提交',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch (error) {
        if (error === 'cancel') {
          statusUpdating.value = false
          return
        }
      }
    }
    
    const { shot, importantNotes } = await shotStore.updateShotStatus(props.shot.id, newStatus.value)
    
    // 显示成功消息
    ElMessage.success('状态更新成功')
    
    // 更新父组件显示
    emit('update', shot)
    
    // 重置状态
    newStatus.value = ''
  } catch (error) {
    console.error('更新状态失败', error)
    ElMessage.error('更新状态失败')
  } finally {
    statusUpdating.value = false
  }
}

// 关闭详情面板
const closeDetails = () => {
  emit('close')
}

// 监听镜头变化
watch(() => props.shot, (newShot) => {
  if (newShot && newShot.id) {
    loadComments()
    loadNotes()
  }
}, { immediate: true })

onMounted(() => {
  if (props.shot && props.shot.id) {
    loadComments()
    loadNotes()
  }
})
</script>

<style scoped>
.shot-details {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-left: 1px solid #f0f0f0;
  background-color: #ffffff;
}

.shot-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.shot-title {
  margin: 0;
  font-size: 18px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.shot-details-content {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-card {
  margin-bottom: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shot-info {
  padding: 8px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.info-row:first-child {
  margin-top: 2px;
}

.info-row .info-item {
  flex: 1;
  padding-right: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-description {
  margin-top: 8px;
  border-top: 1px dashed #ebeef5;
  padding-top: 8px;
}

.info-label {
  font-size: 0.7em;
  color: #909399;
  margin-bottom: 2px;
}

.info-value {
  word-break: break-word;
}

.description {
  white-space: pre-line;
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.status-update {
  display: flex;
  gap: 12px;
}

.status-select {
  flex: 1;
}

.text-danger {
  color: #F56C6C;
}

.text-warning {
  color: #E6A23C;
}

.loading-placeholder,
.empty-placeholder {
  padding: 16px 0;
}

.comment-list,
.note-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item,
.note-item {
  padding: 12px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.important-note {
  background-color: #fef0f0;
}

.comment-header,
.note-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.comment-user,
.note-user {
  font-weight: bold;
}

.comment-time,
.note-time {
  color: #909399;
  font-size: 12px;
}

.comment-content,
.note-content {
  margin-bottom: 8px;
  white-space: pre-line;
}

.comment-status,
.comment-actions,
.note-actions {
  display: flex;
  justify-content: flex-end;
}

.important-tag {
  margin-right: 8px;
}

.important-hint {
  color: #F56C6C;
  font-size: 12px;
}

.status-update-dialog {
  padding: 16px;
}

.status-select-full {
  width: 100%;
}

.frame-rate {
  font-style: italic;
  font-size: 0.9em;
  color: #909399;
  margin-left: 2px;
}

.el-tag {
  padding: 0 6px;
  height: 22px;
  line-height: 20px;
}
</style> 