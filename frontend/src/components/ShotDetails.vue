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
              <el-button v-if="canAddComment" type="primary" size="small" plain @click="showAddCommentDialog">
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
              
              <!-- 附件显示 -->
              <div v-if="comment.attachments && comment.attachments.length > 0" class="comment-attachments">
                <div class="attachments-title">附件：</div>
                <div class="attachments-list">
                  <div v-for="attachment in comment.attachments" :key="attachment.id" class="attachment-item">
                    <!-- 添加日志 -->
                    {{ console.log('Comment Attachment SRC:', attachment.thumbnail_path || attachment.file_path) }}
                    <a v-if="attachment.is_image" :href="attachment.file_path" target="_blank" class="attachment-link">
                      <img :src="attachment.thumbnail_path || attachment.file_path" :alt="attachment.file_name" class="attachment-thumbnail" />
                    </a>
                    <a v-else :href="attachment.file_path" target="_blank" class="attachment-link">
                      <div class="attachment-file">
                        <el-icon><Document /></el-icon>
                        <span class="attachment-name">{{ attachment.file_name }}</span>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
              
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
            :before-close="handleCommentDialogClose"
          >
            <el-form ref="commentFormRef" :model="commentForm" :rules="commentRules">
              <el-form-item prop="content" label="反馈内容">
                <el-input
                  v-model="commentForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入反馈内容"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="附件">
                <el-upload
                  class="upload-demo"
                  action="#"
                  :auto-upload="false"
                  :on-change="handleCommentFileChange"
                  :on-remove="handleCommentFileRemove"
                  multiple
                  :file-list="commentFileList"
                >
                  <el-button type="primary">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持任意类型文件，图片将生成缩略图
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="closeCommentDialog">取消</el-button>
              <el-button 
                type="primary" 
                :loading="commentSubmitting"
                @click="submitComment"
                :disabled="!commentForm.content || !commentForm.content.trim()"
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
              <el-button type="primary" size="small" plain @click="showAddNoteDialog">
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
              
              <!-- 附件显示 -->
              <div v-if="note.attachments && note.attachments.length > 0" class="note-attachments">
                <div class="attachments-title">附件：</div>
                <div class="attachments-list">
                  <div v-for="attachment in note.attachments" :key="attachment.id" class="attachment-item">
                    <!-- 添加日志 -->
                    {{ console.log('Note Attachment SRC:', attachment.thumbnail_path || attachment.file_path) }}
                    <a v-if="attachment.is_image" :href="attachment.file_path" target="_blank" class="attachment-link">
                      <img :src="attachment.thumbnail_path || attachment.file_path" :alt="attachment.file_name" class="attachment-thumbnail" />
                    </a>
                    <a v-else :href="attachment.file_path" target="_blank" class="attachment-link">
                      <div class="attachment-file">
                        <el-icon><Document /></el-icon>
                        <span class="attachment-name">{{ attachment.file_name }}</span>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
              
              <div v-if="canDeleteNote(note)" class="note-actions">
                <el-button type="link" size="small" @click="deleteNote(note.id)">
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
            :before-close="handleNoteDialogClose"
          >
            <el-form ref="noteFormRef" :model="noteForm" :rules="noteRules">
              <el-form-item prop="content" label="备注内容">
                <el-input
                  v-model="noteForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入备注内容"
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item>
                <el-checkbox v-model="noteForm.is_important">
                  标记为重要提示 <span class="important-hint">(提交状态变更时将提示确认)</span>
                </el-checkbox>
              </el-form-item>
              <el-form-item label="附件">
                <el-upload
                  class="upload-demo"
                  action="#"
                  :auto-upload="false"
                  :on-change="handleNoteFileChange"
                  :on-remove="handleNoteFileRemove"
                  multiple
                  :file-list="noteFileList"
                >
                  <el-button type="primary">选择文件</el-button>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持任意类型文件，图片将生成缩略图
                    </div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="closeNoteDialog">取消</el-button>
              <el-button 
                type="primary" 
                :loading="noteSubmitting"
                @click="submitNote"
                :disabled="!noteForm.content || !noteForm.content.trim()"
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close, Edit, Plus, RefreshRight, Document } from '@element-plus/icons-vue'
import { useShotStore } from '@/stores/shotStore'
import { useAuthStore } from '@/stores/authStore'
import shotService from '@/services/shotService'
import { formatDate, formatDateTime, getDeadlineClass, getSubmitDateClass } from '@/utils/dateUtils'
import { getStatusTagType, getStageTagType } from '@/utils/statusUtils'
import { formatAttachments } from '@/utils/mediaHelper'

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
const commentFormRef = ref(null)
const noteFormRef = ref(null)
const commentFileList = ref([])
const noteFileList = ref([])

// 表单
const commentForm = ref({
  content: '',
  attachment_data: []
})

const noteForm = ref({
  content: '',
  is_important: false,
  attachment_data: []
})

// 对话框处理
const handleCommentDialogClose = (done) => {
  if (commentSubmitting.value) {
    return
  }
  closeCommentDialog()
  done()
}

const handleNoteDialogClose = (done) => {
  if (noteSubmitting.value) {
    return
  }
  closeNoteDialog()
  done()
}

const closeCommentDialog = () => {
  showAddComment.value = false
  commentFileList.value = []
  commentForm.value = {
    content: '',
    attachment_data: []
  }
}

const closeNoteDialog = () => {
  showAddNote.value = false
  noteFileList.value = []
  noteForm.value = {
    content: '',
    is_important: false,
    attachment_data: []
  }
}

// 文件处理函数
const handleCommentFileChange = (file) => {
  if (!file || !file.raw) {
    console.error('文件对象无效', file)
    return
  }

  // 如果文件过大，提示并返回
  const maxSizeInBytes = 5 * 1024 * 1024 // 5MB，压缩后端允许的大小
  if (file.size > maxSizeInBytes) {
    ElMessage.warning(`文件大小不能超过5MB：${file.name}`)
    return
  }

  try {
    // 处理上传的文件
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        if (!e.target || !e.target.result) {
          console.error('读取文件失败：无结果')
          return
        }
        
        const fileData = {
          file_name: file.name,
          file_content: e.target.result,
          file_size: file.size
        }
        commentForm.value.attachment_data.push(fileData)
        console.log('文件处理成功，大小:', Math.round(file.size / 1024), 'KB')
      } catch (error) {
        console.error('处理文件数据错误', error)
        ElMessage.error(`处理文件出错: ${file.name}`)
      }
    }
    reader.onerror = (error) => {
      console.error('读取文件错误', error)
      ElMessage.error(`读取文件失败: ${file.name}`)
    }
    reader.readAsDataURL(file.raw)
  } catch (error) {
    console.error('文件上传预处理错误', error)
    ElMessage.error(`文件处理错误: ${file.name}`)
  }
}

const handleCommentFileRemove = (file) => {
  try {
    const index = commentForm.value.attachment_data.findIndex(f => f.file_name === file.name)
    if (index !== -1) {
      commentForm.value.attachment_data.splice(index, 1)
    }
  } catch (error) {
    console.error('移除文件错误', error)
  }
}

const handleNoteFileChange = (file) => {
  if (!file || !file.raw) {
    console.error('文件对象无效', file)
    return
  }

  // 如果文件过大，提示并返回
  const maxSizeInBytes = 5 * 1024 * 1024 // 5MB，压缩后端允许的大小
  if (file.size > maxSizeInBytes) {
    ElMessage.warning(`文件大小不能超过5MB：${file.name}`)
    return
  }

  try {
    // 处理上传的文件
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        if (!e.target || !e.target.result) {
          console.error('读取文件失败：无结果')
          return
        }
        
        const fileData = {
          file_name: file.name,
          file_content: e.target.result,
          file_size: file.size
        }
        noteForm.value.attachment_data.push(fileData)
        console.log('文件处理成功，大小:', Math.round(file.size / 1024), 'KB')
      } catch (error) {
        console.error('处理文件数据错误', error)
        ElMessage.error(`处理文件出错: ${file.name}`)
      }
    }
    reader.onerror = (error) => {
      console.error('读取文件错误', error)
      ElMessage.error(`读取文件失败: ${file.name}`)
    }
    reader.readAsDataURL(file.raw)
  } catch (error) {
    console.error('文件上传预处理错误', error)
    ElMessage.error(`文件处理错误: ${file.name}`)
  }
}

const handleNoteFileRemove = (file) => {
  try {
    const index = noteForm.value.attachment_data.findIndex(f => f.file_name === file.name)
    if (index !== -1) {
      noteForm.value.attachment_data.splice(index, 1)
    }
  } catch (error) {
    console.error('移除文件错误', error)
  }
}

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
  return authStore.canEditShot(props.shot)
})

const canAddComment = computed(() => {
  // 所有登录用户都可以添加反馈
  return true
})

const canUpdateStatus = computed(() => {
  return authStore.canEditShot(props.shot)
})

const canResolveComment = (comment) => {
  return authStore.isAdmin || authStore.isManager || comment.user === authStore.user?.id
}

const canDeleteNote = (note) => {
  return authStore.isAdmin || authStore.isManager || note.user === authStore.user?.id
}

// 加载评论
const loadComments = async () => {
  if (!props.shot || !props.shot.id) return
  
  console.log('加载镜头ID为', props.shot.id, '的备注')
  commentsLoading.value = true
  
  try {
    const response = await shotService.getShotComments(props.shot.id)
    console.log('获取到备注响应:', response.data)
    
    // 处理附件URL，确保使用正确的协议和端口
    if (response.data && response.data.results) {
      response.data.results.forEach(comment => {
        if (comment.attachments && comment.attachments.length > 0) {
          comment.attachments = formatAttachments(comment.attachments);
        }
      });
    }
    
    comments.value = response.data.results || []
  } catch (error) {
    console.error('获取镜头备注失败', error)
    ElMessage.error('获取镜头备注失败')
  } finally {
    commentsLoading.value = false
  }
}

// 加载备注
const loadNotes = async () => {
  if (!props.shot || !props.shot.id) return
  
  notesLoading.value = true
  
  try {
    const response = await shotService.getShotNotes(props.shot.id)
    
    // 处理附件URL，确保使用正确的协议和端口
    if (response.data && response.data.results) {
      response.data.results.forEach(note => {
        if (note.attachments && note.attachments.length > 0) {
          note.attachments = formatAttachments(note.attachments);
        }
      });
    }
    
    notes.value = response.data.results || []
  } catch (error) {
    console.error('获取镜头备注失败', error)
    ElMessage.error('获取镜头备注失败')
  } finally {
    notesLoading.value = false
  }
}

// 提交反馈
const submitComment = async () => {
  if (!commentForm.value.content || !commentForm.value.content.trim()) {
    ElMessage.warning('请输入反馈内容')
    return
  }

  try {
    commentSubmitting.value = true
    
    // 准备提交数据
    const data = {
      content: commentForm.value.content.trim()
    }
    
    // 如果有附件数据，且不为空，才添加到请求中
    if (commentForm.value.attachment_data && commentForm.value.attachment_data.length > 0) {
      data.attachment_data = commentForm.value.attachment_data
    }
    
    // 提交到后端
    console.log('提交反馈数据:', JSON.stringify(data, null, 2))
    const response = await shotService.addShotComment(props.shot.id, data)
    console.log('反馈提交成功:', response.data)
    
    // 关闭对话框并清空表单
    closeCommentDialog()
    
    // 重新加载反馈
    await loadComments()
    
    ElMessage.success('反馈添加成功')
  } catch (error) {
    console.error('添加反馈失败', error)
    let errorMsg = '未知错误'
    if (error.response) {
      console.error('错误响应:', error.response.data)
      errorMsg = error.response.data?.detail || 
                error.response.data?.message || 
                `服务器错误: ${error.response.status}`
    } else if (error.request) {
      errorMsg = '服务器未响应，请检查网络连接'
    } else {
      errorMsg = error.message || '请求配置错误'
    }
    ElMessage.error('添加反馈失败: ' + errorMsg)
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
  if (!noteForm.value.content || !noteForm.value.content.trim()) {
    ElMessage.warning('请输入备注内容')
    return
  }

  try {
    noteSubmitting.value = true
    
    // 准备提交数据，不包含shot字段，因为已经在URL中
    const data = {
      content: noteForm.value.content.trim(),
      is_important: noteForm.value.is_important
    }
    
    // 如果有附件数据，且不为空，才添加到请求中
    if (noteForm.value.attachment_data && noteForm.value.attachment_data.length > 0) {
      data.attachment_data = noteForm.value.attachment_data
    }
    
    // 提交到后端
    console.log('提交备注数据:', JSON.stringify(data, null, 2))
    const response = await shotService.addShotNote(props.shot.id, data)
    console.log('备注提交成功:', response.data)
    
    closeNoteDialog()
    await loadNotes()
    
    // 尝试获取更新后的镜头数据
    try {
      const updatedShot = await shotStore.fetchShot(props.shot.id)
      // 仅在成功获取到 updatedShot 后才 emit 事件
      if (updatedShot) {
        emit('update', updatedShot)
      } else {
        console.warn('获取更新后的镜头数据失败，未触发 update 事件')
      }
    } catch (fetchError) {
      console.error('获取更新后的镜头数据时出错:', fetchError)
      // 即使获取失败，也提示备注添加成功，但可能不会立即更新列表中的某些信息
    }
    
    ElMessage.success('备注添加成功')
  } catch (error) {
    console.error('添加备注失败', error)
    let errorMsg = '未知错误'
    if (error.response) {
      console.error('错误响应:', error.response.data)
      errorMsg = error.response.data?.detail || 
                error.response.data?.message || 
                error.response.data || 
                `服务器错误: ${error.response.status}`
    } else if (error.request) {
      errorMsg = '服务器未响应，请检查网络连接'
    } else {
      errorMsg = error.message || '请求配置错误'
    }
    ElMessage.error('添加备注失败: ' + errorMsg)
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

// 打开添加反馈对话框
const showAddCommentDialog = () => {
  // 重置表单
  commentForm.value = {
    content: '',
    attachment_data: []
  }
  commentFileList.value = []
  // 延迟一帧后显示对话框，确保DOM更新
  nextTick(() => {
    showAddComment.value = true
  })
}

// 打开添加备注对话框
const showAddNoteDialog = () => {
  // 重置表单
  noteForm.value = {
    content: '',
    is_important: false,
    attachment_data: []
  }
  noteFileList.value = []
  // 延迟一帧后显示对话框，确保DOM更新
  nextTick(() => {
    showAddNote.value = true
  })
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

.comment-attachments,
.note-attachments {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #ebeef5;
}

.attachments-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.attachment-item {
  width: 80px;
  height: 80px;
  position: relative;
  overflow: hidden;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.attachment-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.attachment-file {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
}

.attachment-name {
  font-size: 10px;
  margin-top: 4px;
  text-align: center;
  width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 4px;
}

.attachment-link {
  display: block;
  width: 100%;
  height: 100%;
  text-decoration: none;
  color: inherit;
}
</style> 