<template>
  <div class="shot-details-wrapper" v-loading="loading">
    <template v-if="shot">
      <div class="shot-header">
        <h2>{{ shot.shot_code }}</h2>
        <div class="shot-actions">
          <el-button 
            type="primary" 
            @click="submitShot" 
            :disabled="shot.status === 'review' || shot.status === 'approved'"
          >
            提交审核
          </el-button>
          <el-button @click="editMode = !editMode">
            {{ editMode ? '取消编辑' : '编辑' }}
          </el-button>
        </div>
      </div>
      
      <!-- 镜头基本信息 -->
      <el-card class="shot-info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button 
              v-if="editMode" 
              type="primary" 
              size="small" 
              @click="saveChanges"
              :loading="saving"
            >
              保存变更
            </el-button>
          </div>
        </template>
        
        <el-form 
          label-position="right" 
          label-width="120px"
          :disabled="!editMode"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="项目">
                <el-input v-if="editMode" v-model="editForm.project_name" disabled />
                <span v-else>{{ shot.project.name }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="镜头编号">
                <el-input v-if="editMode" v-model="editForm.shot_code" />
                <span v-else>{{ shot.shot_code }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="推进阶段">
                <el-select v-if="editMode" v-model="editForm.prom_stage" placeholder="选择推进阶段">
                  <el-option label="布局" value="layout" />
                  <el-option label="动画" value="animation" />
                  <el-option label="灯光" value="lighting" />
                  <el-option label="渲染" value="rendering" />
                </el-select>
                <span v-else>{{ shot.prom_stage }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="制作状态">
                <el-select v-if="editMode" v-model="editForm.status" placeholder="选择状态">
                  <el-option label="制作中" value="in_progress" />
                  <el-option label="审核中" value="review" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="需修改" value="need_revision" />
                </el-select>
                <el-tag v-else :type="getStatusTagType(shot.status)">
                  {{ getStatusText(shot.status) }}
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="制作者">
                <el-select 
                  v-if="editMode" 
                  v-model="editForm.artist_id" 
                  placeholder="选择制作者"
                  filterable
                >
                  <el-option
                    v-for="artist in artists"
                    :key="artist.id"
                    :label="artist.username"
                    :value="artist.id"
                  />
                </el-select>
                <span v-else>{{ shot.artist ? shot.artist.username : '-' }}</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="帧数">
                <el-input-number 
                  v-if="editMode" 
                  v-model="editForm.duration_frame" 
                  :min="1" 
                  controls-position="right"
                />
                <span v-else>{{ shot.duration_frame }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="截止日期">
                <el-date-picker
                  v-if="editMode"
                  v-model="editForm.deadline"
                  type="date"
                  placeholder="选择截止日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
                <span 
                  v-else 
                  :class="getDeadlineClass"
                >
                  {{ shot.deadline || '-' }}
                </span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最近提交日期">
                <span>{{ shot.last_submit_date || '-' }}</span>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="描述">
            <el-input 
              v-if="editMode" 
              v-model="editForm.description" 
              type="textarea" 
              :rows="3" 
            />
            <p v-else class="shot-description">{{ shot.description || '暂无描述' }}</p>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 镜头备注 -->
      <el-card class="shot-notes-card">
        <template #header>
          <div class="card-header">
            <span>镜头备注</span>
            <el-button 
              type="primary" 
              size="small" 
              @click="addNoteVisible = true"
            >
              添加备注
            </el-button>
          </div>
        </template>
        
        <div v-if="shotNotes.length === 0" class="empty-notes">
          还没有镜头备注
        </div>
        
        <el-timeline v-else>
          <el-timeline-item
            v-for="note in shotNotes"
            :key="note.id"
            :timestamp="formatDate(note.created_at)"
            :type="note.is_important ? 'danger' : ''"
          >
            <el-card class="timeline-note-card">
              <template #header>
                <div class="note-header">
                  <div>
                    <span class="note-author">{{ note.user.username }}</span>
                    <el-tag v-if="note.is_important" type="danger" size="small">重要</el-tag>
                  </div>
                  <div>
                    <el-button
                      type="danger"
                      size="small"
                      plain
                      icon="Delete"
                      @click="deleteNote(note.id)"
                      circle
                    />
                  </div>
                </div>
              </template>
              <p class="note-content">{{ note.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
      
      <!-- 镜头反馈 -->
      <el-card class="shot-comments-card">
        <template #header>
          <div class="card-header">
            <span>镜头反馈</span>
          </div>
        </template>
        
        <div v-if="!comments || comments.length === 0" class="empty-comments">
          还没有反馈信息
        </div>
        
        <el-timeline v-else>
          <el-timeline-item
            v-for="comment in comments"
            :key="comment.id"
            :timestamp="formatDate(comment.timestamp)"
            :type="comment.is_resolved ? 'success' : 'primary'"
          >
            <el-card>
              <template #header>
                <div class="comment-header">
                  <span class="comment-author">{{ comment.user.username }}</span>
                  <el-tag v-if="comment.is_resolved" type="success" size="small">已解决</el-tag>
                </div>
              </template>
              <p>{{ comment.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>
    
    <div v-else-if="!loading" class="no-shot-selected">
      <el-empty description="请选择一个镜头" />
    </div>
    
    <!-- 添加备注弹窗 -->
    <el-dialog
      v-model="addNoteVisible"
      title="添加镜头备注"
      width="500px"
    >
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="备注内容" required>
          <el-input 
            v-model="noteForm.content" 
            type="textarea" 
            :rows="5" 
            placeholder="请输入备注内容..."
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="noteForm.is_important">
            标记为重要提示（提交时将提醒制作人）
          </el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addNoteVisible = false">取消</el-button>
          <el-button type="primary" @click="submitNote" :loading="savingNote">
            添加
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 重要备注确认弹窗 -->
    <el-dialog
      v-model="confirmSubmitVisible"
      title="重要备注确认"
      width="500px"
    >
      <div class="important-notes-warning">
        <el-alert
          type="warning"
          :closable="false"
          show-icon
        >
          <p>此镜头存在重要备注，请确认是否继续提交</p>
        </el-alert>
        
        <div class="important-notes-list">
          <div 
            v-for="note in importantNotes" 
            :key="note.id"
            class="important-note-item"
          >
            <p><strong>{{ note.user.username }}</strong> - {{ formatDate(note.created_at) }}</p>
            <p>{{ note.content }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="confirmSubmitVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSubmit" :loading="submitting">
            确认提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useShotStore } from '@/stores/shotStore';
import { useCommentStore } from '@/stores/commentStore';
import { useUserStore } from '@/stores/userStore';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Delete } from '@element-plus/icons-vue';
import { formatDistance, parseISO } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// Props
const props = defineProps({
  shotId: {
    type: [Number, String],
    default: null
  }
});

// Stores
const shotStore = useShotStore();
const commentStore = useCommentStore();
const userStore = useUserStore();

// State
const loading = computed(() => shotStore.loading);
const shot = computed(() => shotStore.selectedShot);
const shotNotes = computed(() => shotStore.shotNotes);
const comments = ref([]);
const editMode = ref(false);
const saving = ref(false);
const addNoteVisible = ref(false);
const savingNote = ref(false);
const confirmSubmitVisible = ref(false);
const importantNotes = ref([]);
const submitting = ref(false);
const artists = ref([]);

// Form data
const editForm = ref({
  shot_code: '',
  prom_stage: '',
  status: '',
  artist_id: null,
  duration_frame: 0,
  deadline: '',
  description: '',
  project_name: ''
});

const noteForm = ref({
  content: '',
  is_important: false
});

// Computed
const getDeadlineClass = computed(() => {
  if (!shot.value || !shot.value.deadline) return '';
  
  const today = new Date();
  const deadline = new Date(shot.value.deadline);
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) {
    // 已过期
    return shot.value.last_submit_date ? 'deadline-late' : 'deadline-expired';
  } else if (diffDays <= 3) {
    // 即将到期
    return 'deadline-approaching';
  }
  
  return '';
});

// Watch for shot ID changes
watch(() => props.shotId, async (newId) => {
  if (newId) {
    await loadShotDetails(newId);
  } else {
    shotStore.selectedShot = null;
  }
}, { immediate: true });

// Watch shot data to update form
watch(shot, (newShot) => {
  if (newShot) {
    editForm.value = {
      shot_code: newShot.shot_code,
      prom_stage: newShot.prom_stage,
      status: newShot.status,
      artist_id: newShot.artist?.id,
      duration_frame: newShot.duration_frame,
      deadline: newShot.deadline,
      description: newShot.description,
      project_name: newShot.project.name
    };
  }
});

// Load data on mount
onMounted(async () => {
  await fetchArtists();
});

// Methods
async function loadShotDetails(id) {
  try {
    await shotStore.fetchShotById(id);
    await shotStore.fetchShotNotes(id);
    await fetchComments(id);
  } catch (error) {
    ElMessage.error('加载镜头详情失败');
  }
}

async function fetchComments(shotId) {
  try {
    const response = await commentStore.fetchShotComments(shotId);
    comments.value = response || [];
  } catch (error) {
    console.error('获取反馈失败:', error);
    ElMessage.error('获取镜头反馈失败');
    comments.value = [];
  }
}

async function fetchArtists() {
  try {
    const response = await userStore.fetchUsers({ role: 'artist' });
    artists.value = response || [];
  } catch (error) {
    console.error('获取制作者列表失败:', error);
    ElMessage.error('获取制作者列表失败');
  }
}

function formatDate(dateString) {
  if (!dateString) return '';
  
  try {
    const date = parseISO(dateString);
    return formatDistance(date, new Date(), { 
      addSuffix: true,
      locale: zhCN
    });
  } catch (error) {
    return dateString;
  }
}

async function saveChanges() {
  if (!shot.value) return;
  
  saving.value = true;
  try {
    await shotStore.updateShot(shot.value.id, editForm.value);
    ElMessage.success('保存成功');
    editMode.value = false;
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败: ' + (error.message || '未知错误'));
  } finally {
    saving.value = false;
  }
}

async function submitNote() {
  if (!noteForm.value.content.trim()) {
    ElMessage.warning('请输入备注内容');
    return;
  }
  
  if (!shot.value) return;
  
  savingNote.value = true;
  try {
    await shotStore.createShotNote({
      shot: shot.value.id,
      content: noteForm.value.content,
      is_important: noteForm.value.is_important
    });
    
    ElMessage.success('添加备注成功');
    addNoteVisible.value = false;
    noteForm.value = {
      content: '',
      is_important: false
    };
  } catch (error) {
    console.error('添加备注失败:', error);
    ElMessage.error('添加备注失败: ' + (error.message || '未知错误'));
  } finally {
    savingNote.value = false;
  }
}

async function deleteNote(noteId) {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条备注吗？此操作不可恢复',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await shotStore.deleteShotNote(noteId);
    ElMessage.success('删除成功');
    
    // 重新加载备注列表
    if (shot.value) {
      await shotStore.fetchShotNotes(shot.value.id);
    }
  } catch (error) {
    if (error === 'cancel') return;
    console.error('删除备注失败:', error);
    ElMessage.error('删除备注失败: ' + (error.message || '未知错误'));
  }
}

async function submitShot() {
  if (!shot.value) return;
  
  try {
    const response = await shotStore.submitShot(shot.value.id);
    
    // 检查是否有重要备注需要确认
    if (response.important_notes) {
      importantNotes.value = response.important_notes;
      confirmSubmitVisible.value = true;
      return;
    }
    
    ElMessage.success('镜头已成功提交');
  } catch (error) {
    console.error('提交镜头失败:', error);
    ElMessage.error('提交镜头失败: ' + (error.message || '未知错误'));
  }
}

async function confirmSubmit() {
  if (!shot.value) return;
  
  submitting.value = true;
  try {
    // 二次确认提交
    const response = await shotStore.updateShot(shot.value.id, {
      status: 'review',
      last_submit_date: new Date().toISOString().split('T')[0]
    });
    
    ElMessage.success('镜头已成功提交');
    confirmSubmitVisible.value = false;
  } catch (error) {
    console.error('提交镜头失败:', error);
    ElMessage.error('提交镜头失败: ' + (error.message || '未知错误'));
  } finally {
    submitting.value = false;
  }
}

function getStatusText(status) {
  return shotStore.getStatusText(status);
}

function getStatusTagType(status) {
  const typeMap = {
    'in_progress': '',
    'review': 'warning',
    'approved': 'success',
    'need_revision': 'danger'
  };
  return typeMap[status] || '';
}
</script>

<style scoped>
.shot-details-wrapper {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.shot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.shot-actions {
  display: flex;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shot-info-card {
  margin-bottom: 24px;
}

.shot-notes-card {
  margin-bottom: 24px;
}

.shot-comments-card {
  margin-bottom: 24px;
}

.shot-description {
  white-space: pre-line;
  color: #606266;
}

.empty-notes, .empty-comments {
  color: #909399;
  text-align: center;
  padding: 20px;
}

.no-shot-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-author, .comment-author {
  font-weight: bold;
  margin-right: 8px;
}

.note-content {
  white-space: pre-line;
}

.comment-header {
  display: flex;
  align-items: center;
}

.timeline-note-card {
  --el-card-padding: 12px;
}

.deadline-expired {
  color: #F56C6C;
  font-weight: bold;
}

.deadline-late {
  color: #E6A23C;
  font-weight: bold;
}

.deadline-approaching {
  color: #E6A23C;
}

.important-notes-warning {
  margin-bottom: 20px;
}

.important-notes-list {
  margin-top: 16px;
  max-height: 250px;
  overflow-y: auto;
}

.important-note-item {
  padding: 12px;
  border-bottom: 1px solid #EBEEF5;
}

.important-note-item:last-child {
  border-bottom: none;
}
</style> 