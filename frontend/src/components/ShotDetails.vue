<template>
  <div class="shot-details">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本信息" name="info">
        <div class="details-content">
          <div v-if="isEditing">
            <!-- 编辑模式 -->
            <el-form :model="editForm" label-width="100px" :rules="rules" ref="formRef">
              <el-form-item label="镜头编号" prop="shot_code">
                <el-input v-model="editForm.shot_code" placeholder="请输入镜头编号" />
              </el-form-item>
              
              <el-form-item label="状态" prop="status">
                <el-select v-model="editForm.status" placeholder="请选择状态">
                  <el-option label="制作中" value="in_progress" />
                  <el-option label="审核中" value="review" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="需修改" value="need_revision" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="截止日期" prop="deadline">
                <el-date-picker
                  v-model="editForm.deadline"
                  type="date"
                  placeholder="选择截止日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </el-form-item>
              
              <el-form-item label="时长(帧)" prop="duration_frame">
                <el-input-number v-model="editForm.duration_frame" :min="1" />
              </el-form-item>
              
              <el-form-item label="推进阶段" prop="prom_stage">
                <el-input v-model="editForm.prom_stage" placeholder="请输入推进阶段" />
              </el-form-item>
              
              <el-form-item label="描述" prop="description">
                <el-input
                  v-model="editForm.description"
                  type="textarea"
                  rows="3"
                  placeholder="请输入镜头描述"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveShot">保存</el-button>
                <el-button @click="cancelEdit">取消</el-button>
              </el-form-item>
            </el-form>
          </div>
          
          <div v-else>
            <!-- 查看模式 -->
            <div class="shot-header">
              <div class="shot-title">
                <h2>{{ shot.shot_code }}</h2>
                <el-tag :type="getStatusType(shot.status)" size="large">
                  {{ getStatusText(shot.status) }}
                </el-tag>
              </div>
              <div class="shot-actions">
                <el-button type="primary" @click="startEdit">编辑</el-button>
              </div>
            </div>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="项目">
                {{ shot.project_code || '未知项目' }}
              </el-descriptions-item>
              
              <el-descriptions-item label="截止日期">
                <span :class="{ 'overdue': isOverdue(shot.deadline) }">
                  {{ formatDate(shot.deadline) || '无' }}
                </span>
              </el-descriptions-item>
              
              <el-descriptions-item label="时长">
                {{ shot.duration_frame ? `${shot.duration_frame} 帧` : '未设置' }}
              </el-descriptions-item>
              
              <el-descriptions-item label="推进阶段">
                {{ shot.prom_stage || '未设置' }}
              </el-descriptions-item>
              
              <el-descriptions-item label="创建时间">
                {{ formatDateTime(shot.created_at) }}
              </el-descriptions-item>
              
              <el-descriptions-item label="更新时间">
                {{ formatDateTime(shot.updated_at) }}
              </el-descriptions-item>
              
              <el-descriptions-item label="描述" :span="2">
                {{ shot.description || '无描述' }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="反馈" name="comments">
        <div class="comments-section">
          <div class="comments-list" v-loading="loadingComments">
            <div v-if="comments.length === 0" class="no-comments">
              <el-empty description="暂无反馈" />
            </div>
            
            <div v-else class="comment-item" v-for="comment in comments" :key="comment.id">
              <div class="comment-header">
                <div class="user-info">
                  <el-avatar :size="32" :src="comment.user_avatar">
                    {{ comment.user_username?.charAt(0).toUpperCase() }}
                  </el-avatar>
                  <span class="username">{{ comment.user_username }}</span>
                </div>
                <div class="comment-time">
                  {{ formatDateTime(comment.timestamp) }}
                </div>
              </div>
              
              <div class="comment-content">
                {{ comment.content }}
              </div>
              
              <div class="comment-footer" v-if="comment.attachments?.length">
                <div class="attachments">
                  <div 
                    v-for="attachment in comment.attachments" 
                    :key="attachment.id"
                    class="attachment-item"
                  >
                    <el-link :href="attachment.file_path" target="_blank">
                      {{ attachment.file_name }}
                    </el-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="comment-form">
            <h3>添加反馈</h3>
            <el-form :model="commentForm" :rules="commentRules" ref="commentFormRef">
              <el-form-item prop="content">
                <el-input
                  v-model="commentForm.content"
                  type="textarea"
                  rows="3"
                  placeholder="请输入反馈内容，可以使用@提及其他用户"
                />
              </el-form-item>
              
              <el-form-item>
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleFileChange"
                  :on-remove="handleFileRemove"
                  :file-list="fileList"
                  multiple
                >
                  <el-button type="primary">选择附件</el-button>
                </el-upload>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="submitComment" :loading="submittingComment">
                  提交反馈
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { format, isAfter } from 'date-fns'
import { useShotStore } from '../stores/shotStore'
import shotService from '../services/shotService'
import commentService from '../services/commentService'

const props = defineProps({
  shot: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:shot', 'close'])

// 状态变量
const activeTab = ref('info')
const isEditing = ref(false)
const loadingComments = ref(false)
const submittingComment = ref(false)
const comments = ref([])
const fileList = ref([])
const shotStore = useShotStore()
const formRef = ref(null)
const commentFormRef = ref(null)

// 表单数据
const editForm = reactive({
  shot_code: '',
  status: '',
  deadline: null,
  duration_frame: null,
  prom_stage: '',
  description: ''
})

// 评论表单
const commentForm = reactive({
  content: ''
})

// 表单验证规则
const rules = {
  shot_code: [
    { required: true, message: '请输入镜头编号', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

const commentRules = {
  content: [
    { required: true, message: '请输入反馈内容', trigger: 'blur' }
  ]
}

// 计算属性
const isOverdue = (deadline) => {
  if (!deadline) return false
  
  try {
    const deadlineDate = new Date(deadline)
    const today = new Date()
    
    return isAfter(today, deadlineDate)
  } catch (e) {
    return false
  }
}

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
    return format(date, 'yyyy-MM-dd')
  } catch (e) {
    return dateString
  }
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    return format(date, 'yyyy-MM-dd HH:mm')
  } catch (e) {
    return dateString
  }
}

// 开始编辑
const startEdit = () => {
  // 复制当前数据到表单
  Object.keys(editForm).forEach(key => {
    if (props.shot[key] !== undefined) {
      editForm[key] = props.shot[key]
    }
  })
  
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
}

// 保存镜头
const saveShot = async () => {
  try {
    if (!formRef.value) return
    
    await formRef.value.validate()
    
    const shotData = { ...editForm }
    
    // 更新镜头
    const updatedShot = await shotStore.updateShot(props.shot.id, shotData)
    
    isEditing.value = false
    
    // 通知父组件更新
    emit('update:shot', updatedShot)
    
    ElMessage.success('镜头信息已更新')
  } catch (err) {
    console.error('保存镜头失败:', err)
    ElMessage.error('保存失败，请检查表单')
  }
}

// 加载评论
const loadComments = async () => {
  loadingComments.value = true
  
  try {
    const response = await commentService.getComments({ 
      shot: props.shot.id,
      top_level: true
    })
    
    comments.value = response.data
  } catch (err) {
    console.error('加载评论失败:', err)
    ElMessage.error('加载评论失败')
  } finally {
    loadingComments.value = false
  }
}

// 处理文件上传
const handleFileChange = (file) => {
  fileList.value.push(file)
}

// 处理文件移除
const handleFileRemove = (file, fileList) => {
  const index = fileList.value.indexOf(file)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

// 提交评论
const submitComment = async () => {
  try {
    if (!commentFormRef.value) return
    
    await commentFormRef.value.validate()
    
    submittingComment.value = true
    
    // 创建评论
    const commentData = {
      shot: props.shot.id,
      content: commentForm.content
    }
    
    const response = await commentService.createComment(commentData)
    const newComment = response.data
    
    // 上传附件
    if (fileList.value.length > 0) {
      for (const file of fileList.value) {
        const formData = new FormData()
        formData.append('comment', newComment.id)
        formData.append('file_path', file.raw)
        formData.append('file_name', file.name)
        formData.append('file_size', file.size)
        formData.append('mime_type', file.type)
        
        await commentService.uploadAttachment(formData)
      }
    }
    
    // 重新加载评论
    await loadComments()
    
    // 重置表单
    commentForm.content = ''
    fileList.value = []
    
    ElMessage.success('反馈已提交')
  } catch (err) {
    console.error('提交评论失败:', err)
    ElMessage.error('提交失败，请检查表单')
  } finally {
    submittingComment.value = false
  }
}

// 监听标签页切换
const handleTabChange = (tab) => {
  if (tab.name === 'comments') {
    loadComments()
  }
}

// 组件挂载时加载评论
onMounted(() => {
  if (activeTab.value === 'comments') {
    loadComments()
  }
})

// 监听标签页变化
watch(activeTab, (newVal) => {
  if (newVal === 'comments') {
    loadComments()
  }
})
</script>

<style scoped>
.shot-details {
  padding: 20px;
}

.details-content {
  margin-top: 20px;
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.shot-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.shot-title h2 {
  margin: 0;
}

.overdue {
  color: #f56c6c;
  font-weight: bold;
}

.comments-section {
  margin-top: 20px;
}

.comments-list {
  margin-bottom: 30px;
  max-height: 400px;
  overflow-y: auto;
}

.no-comments {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.comment-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: bold;
}

.comment-time {
  color: #909399;
  font-size: 12px;
}

.comment-content {
  white-space: pre-line;
  margin-bottom: 10px;
}

.comment-footer {
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  background-color: #f5f7fa;
  padding: 5px 10px;
  border-radius: 4px;
}

.comment-form {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}
</style> 