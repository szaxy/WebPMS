<template>
  <div class="comment-list-container">
    <div class="comments-header">
      <h3>反馈列表</h3>
      <el-button type="primary" size="small" @click="refreshComments">
        <el-icon><Refresh /></el-icon> 刷新
      </el-button>
    </div>
    
    <div class="comments-list" v-loading="loading">
      <div v-if="comments.length === 0" class="no-comments">
        <el-empty description="暂无反馈" />
      </div>
      
      <el-timeline v-else>
        <el-timeline-item
          v-for="comment in comments"
          :key="comment.id"
          :timestamp="formatDateTime(comment.timestamp)"
          :type="getCommentType(comment)"
        >
          <div class="comment-item">
            <div class="comment-header">
              <div class="user-info">
                <el-avatar :size="32" :src="comment.user_avatar">
                  {{ comment.user_username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ comment.user_username }}</span>
              </div>
              
              <div class="comment-actions">
                <el-button 
                  v-if="canResolve(comment)" 
                  type="success" 
                  size="small" 
                  plain 
                  @click="resolveComment(comment)"
                  :disabled="resolvingId === comment.id"
                >
                  {{ comment.is_resolved ? '标记为未解决' : '标记为已解决' }}
                </el-button>
                
                <el-button
                  size="small"
                  plain
                  @click="replyToComment(comment)"
                >回复</el-button>
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
                  <el-tooltip
                    :content="attachment.file_name"
                    placement="top"
                  >
                    <el-link :href="attachment.file_path" target="_blank">
                      <el-icon><Document /></el-icon>
                      {{ truncateFilename(attachment.file_name) }}
                    </el-link>
                  </el-tooltip>
                </div>
              </div>
            </div>
            
            <!-- 回复列表 -->
            <div class="replies" v-if="comment.replies_count > 0">
              <el-button type="text" @click="loadReplies(comment.id)" v-if="!loadedReplies[comment.id]">
                查看{{ comment.replies_count }}条回复
              </el-button>
              
              <div v-else>
                <div class="replies-list">
                  <div 
                    v-for="reply in repliesMap[comment.id]" 
                    :key="reply.id"
                    class="reply-item"
                  >
                    <div class="reply-header">
                      <div class="user-info">
                        <el-avatar :size="24" :src="reply.user_avatar">
                          {{ reply.user_username?.charAt(0).toUpperCase() }}
                        </el-avatar>
                        <span class="username">{{ reply.user_username }}</span>
                      </div>
                      <span class="reply-time">{{ formatDateTime(reply.timestamp) }}</span>
                    </div>
                    <div class="reply-content">
                      {{ reply.content }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>
    
    <div class="comment-form">
      <h3>{{ replyTo ? '回复反馈' : '添加反馈' }}</h3>
      
      <div v-if="replyTo" class="reply-info">
        <el-alert
          title="正在回复"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="reply-to-info">
              <span>{{ replyTo.user_username }}</span>: {{ truncateText(replyTo.content, 50) }}
              <el-button type="text" @click="cancelReply">取消回复</el-button>
            </div>
          </template>
        </el-alert>
      </div>
      
      <el-form :model="commentForm" :rules="rules" ref="formRef">
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
          <el-button type="primary" @click="submitComment" :loading="submitting">
            {{ replyTo ? '提交回复' : '提交反馈' }}
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { format } from 'date-fns'
import { ElMessage } from 'element-plus'
import { Document, Refresh } from '@element-plus/icons-vue'
import commentService from '../services/commentService'
import { useAuthStore } from '../stores/authStore'

const props = defineProps({
  shotId: {
    type: [Number, String],
    required: true
  }
})

// 状态
const authStore = useAuthStore()
const loading = ref(false)
const submitting = ref(false)
const comments = ref([])
const fileList = ref([])
const formRef = ref(null)
const replyTo = ref(null)
const repliesMap = ref({})
const loadedReplies = ref({})
const resolvingId = ref(null)

// 表单数据
const commentForm = reactive({
  content: ''
})

// 表单验证规则
const rules = {
  content: [
    { required: true, message: '请输入反馈内容', trigger: 'blur' },
    { min: 2, message: '反馈内容至少2个字符', trigger: 'blur' }
  ]
}

// 加载评论
const loadComments = async () => {
  loading.value = true
  
  try {
    const response = await commentService.getComments({ 
      shot: props.shotId,
      top_level: true
    })
    
    comments.value = response.data
  } catch (err) {
    console.error('加载评论失败:', err)
    ElMessage.error('加载评论失败')
  } finally {
    loading.value = false
  }
}

// 加载回复
const loadReplies = async (commentId) => {
  try {
    const response = await commentService.getCommentReplies(commentId)
    repliesMap.value[commentId] = response.data
    loadedReplies.value[commentId] = true
  } catch (err) {
    console.error('加载回复失败:', err)
    ElMessage.error('加载回复失败')
  }
}

// 刷新评论
const refreshComments = () => {
  loadComments()
  repliesMap.value = {}
  loadedReplies.value = {}
}

// 处理文件上传
const handleFileChange = (file) => {
  fileList.value.push(file)
}

// 处理文件移除
const handleFileRemove = (file) => {
  const index = fileList.value.indexOf(file)
  if (index > -1) {
    fileList.value.splice(index, 1)
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

// 获取评论类型
const getCommentType = (comment) => {
  if (comment.is_resolved) {
    return 'success'
  }
  return ''
}

// 检查是否可以解决评论
const canResolve = (comment) => {
  return authStore.isManager || comment.user === authStore.user?.id
}

// 解决评论
const resolveComment = async (comment) => {
  resolvingId.value = comment.id
  
  try {
    await commentService.resolveComment(comment.id, !comment.is_resolved)
    
    // 更新本地状态
    const index = comments.value.findIndex(c => c.id === comment.id)
    if (index > -1) {
      comments.value[index].is_resolved = !comment.is_resolved
    }
    
    ElMessage.success(`评论已${comment.is_resolved ? '标记为未解决' : '标记为已解决'}`)
  } catch (err) {
    console.error('更新评论状态失败:', err)
    ElMessage.error('更新评论状态失败')
  } finally {
    resolvingId.value = null
  }
}

// 回复评论
const replyToComment = (comment) => {
  replyTo.value = comment
  // 滚动到表单
  document.querySelector('.comment-form').scrollIntoView({ behavior: 'smooth' })
}

// 取消回复
const cancelReply = () => {
  replyTo.value = null
}

// 截断文本
const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

// 截断文件名
const truncateFilename = (filename) => {
  if (!filename) return ''
  
  if (filename.length > 20) {
    const ext = filename.split('.').pop()
    return filename.substring(0, 16) + '...' + (ext ? '.' + ext : '')
  }
  
  return filename
}

// 提交评论
const submitComment = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    // 创建评论数据
    const commentData = {
      shot: props.shotId,
      content: commentForm.content
    }
    
    // 如果是回复，添加回复目标
    if (replyTo.value) {
      commentData.reply_to = replyTo.value.id
    }
    
    // 发送请求
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
    
    // 重置表单
    commentForm.content = ''
    fileList.value = []
    
    if (replyTo.value) {
      // 如果是回复，更新回复列表
      if (loadedReplies.value[replyTo.value.id]) {
        await loadReplies(replyTo.value.id)
      }
      
      // 更新回复数量
      const index = comments.value.findIndex(c => c.id === replyTo.value.id)
      if (index > -1) {
        comments.value[index].replies_count++
      }
      
      replyTo.value = null
    } else {
      // 如果是新评论，添加到列表
      await refreshComments()
    }
    
    ElMessage.success(replyTo.value ? '回复已提交' : '反馈已提交')
  } catch (err) {
    console.error('提交评论失败:', err)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 组件挂载时加载评论
onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.comment-list-container {
  padding: 20px;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.comments-header h3 {
  margin: 0;
}

.comments-list {
  margin-bottom: 30px;
}

.no-comments {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.comment-item {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.comment-content {
  white-space: pre-line;
  margin-bottom: 10px;
  line-height: 1.5;
}

.comment-footer {
  margin-top: 10px;
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  background-color: #f0f2f5;
  padding: 5px 10px;
  border-radius: 4px;
}

.replies {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #e8e8e8;
}

.replies-list {
  margin-top: 10px;
}

.reply-item {
  background-color: #f0f2f5;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 8px;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.reply-time {
  font-size: 12px;
  color: #909399;
}

.reply-content {
  white-space: pre-line;
  font-size: 14px;
}

.comment-form {
  margin-top: 30px;
  border-top: 1px solid #e8e8e8;
  padding-top: 20px;
}

.reply-info {
  margin-bottom: 15px;
}

.reply-to-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style> 