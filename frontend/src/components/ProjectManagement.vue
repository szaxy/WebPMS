<template>
  <el-dialog
    v-model="dialogVisible"
    title="项目管理"
    width="900px"
    :close-on-click-modal="false"
  >
    <div class="project-management">
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目..."
          prefix-icon="Search"
          clearable
          @input="filterProjects"
          style="width: 250px"
          size="small"
        />
        <div class="spacer"></div>
        <el-button type="primary" @click="openAddProjectDialog" size="small">
          <el-icon><Plus /></el-icon> 添加项目
        </el-button>
      </div>

      <!-- 项目列表 -->
      <el-table
        v-loading="loading"
        :data="paginatedProjects"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="name" label="项目名称" sortable min-width="180">
          <template #default="{ row }">
            <div class="project-name">
              {{ row.name }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="code" label="项目代号" width="120" sortable />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusDisplay(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="部门" width="180">
          <template #default="{ row }">
            <div class="departments-list">
              <el-tag
                v-for="dept in row.departments"
                :key="dept.department"
                size="small"
                type="info"
                class="department-tag"
              >
                {{ dept.department_display }}
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="日期" width="180">
          <template #default="{ row }">
            <div class="date-info">
              <div v-if="row.start_date">开始: {{ formatDate(row.start_date) }}</div>
              <div v-if="row.end_date">结束: {{ formatDate(row.end_date) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button
                type="primary"
                size="small"
                title="编辑"
                @click="editProject(row)"
                :disabled="isProcessing"
              >
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button
                type="danger"
                size="small"
                title="删除"
                @click="confirmDeleteProject(row)"
                :disabled="isProcessing"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          layout="total, prev, pager, next"
          :total="totalProjects"
          @current-change="handlePageChange"
          background
        />
      </div>
    </div>

    <!-- 添加项目对话框 -->
    <el-dialog
      v-model="addProjectVisible"
      :title="isEditMode ? '编辑项目' : '添加项目'"
      width="650px"
      append-to-body
      :close-on-click-modal="false"
    >
      <el-form
        :model="projectForm"
        label-width="100px"
        ref="projectFormRef"
        :rules="projectRules"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="项目代号" prop="code">
          <el-input v-model="projectForm.code" placeholder="请输入项目代号" />
          <div class="form-hint">项目代号必须以字母开头，只能包含字母、数字和连字符，长度2-10个字符</div>
        </el-form-item>
        
        <el-form-item label="项目状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="进行中" value="in_progress" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="projectForm.start_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="projectForm.end_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="项目部门" prop="department_ids">
          <el-select
            v-model="projectForm.department_ids"
            multiple
            placeholder="请选择项目关联部门"
            style="width: 100%"
          >
            <el-option label="动画" value="animation" />
            <el-option label="后期" value="post" />
            <el-option label="解算" value="fx" />
            <el-option label="制片" value="producer" />
            <el-option label="模型" value="model" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="projectForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="addProjectVisible = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitProjectForm"
          :loading="isProcessing"
        >
          确认
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watchEffect, onMounted } from 'vue'
import { useProjectStore } from '@/stores/projectStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate } from '@/utils/dateUtils'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'

// 接收的属性
const props = defineProps({
  visible: Boolean
})

// 发出的事件
const emit = defineEmits(['update:visible', 'refresh'])

// 状态
const projectStore = useProjectStore()
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})
const loading = computed(() => projectStore.loading)
const isProcessing = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const addProjectVisible = ref(false)
const isEditMode = ref(false)
const projectFormRef = ref(null)

// 项目表单
const projectForm = reactive({
  id: null,
  name: '',
  code: '',
  status: 'in_progress',
  start_date: '',
  end_date: '',
  description: '',
  department_ids: []
})

// 表单验证规则
const projectRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入项目代号', trigger: 'blur' },
    { pattern: /^[A-Za-z][A-Za-z0-9\-]{1,9}$/, message: '项目代号必须以字母开头，只含字母、数字和连字符，长度2-10', trigger: 'blur' }
  ],
  status: [{ required: true, message: '请选择项目状态', trigger: 'change' }]
}

// 计算属性
const filteredProjects = computed(() => {
  if (!projectStore.projects || !Array.isArray(projectStore.projects)) {
    return []
  }
  
  let result = [...projectStore.projects]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(
      p => p.name.toLowerCase().includes(query) ||
           p.code.toLowerCase().includes(query) ||
           (p.description && p.description.toLowerCase().includes(query))
    )
  }
  
  // 排序 - 默认按创建时间倒序
  result.sort((a, b) => {
    return new Date(b.created_at || 0) - new Date(a.created_at || 0)
  })
  
  return result
})

// 总项目数量
const totalProjects = computed(() => filteredProjects.value.length)

// 分页后的项目
const paginatedProjects = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredProjects.value.slice(start, end)
})

// 过滤项目
const filterProjects = () => {
  currentPage.value = 1 // 重置到第一页
}

// 处理页面变化
const handlePageChange = (page) => {
  currentPage.value = page
}

// 状态标签类型
const getStatusTagType = (status) => {
  const map = {
    'in_progress': 'success',
    'paused': 'warning',
    'archived': 'info'
  }
  return map[status] || 'default'
}

// 状态显示文本
const getStatusDisplay = (status) => {
  const map = {
    'in_progress': '进行中',
    'paused': '已暂停',
    'archived': '已归档'
  }
  return map[status] || status
}

// 加载项目列表
const loadProjects = async () => {
  try {
    await projectStore.fetchProjects()
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    console.error('加载项目列表失败', error)
  }
}

// 打开添加项目对话框
const openAddProjectDialog = () => {
  isEditMode.value = false
  resetProjectForm()
  addProjectVisible.value = true
}

// 编辑项目
const editProject = (project) => {
  isEditMode.value = true
  
  // 复制项目数据到表单
  Object.assign(projectForm, {
    id: project.id,
    name: project.name,
    code: project.code,
    status: project.status,
    start_date: project.start_date,
    end_date: project.end_date,
    description: project.description || '',
    department_ids: project.departments?.map(d => d.department) || []
  })
  
  addProjectVisible.value = true
}

// 确认删除项目
const confirmDeleteProject = (project) => {
  ElMessageBox.confirm(
    `确定要删除项目 "${project.name}" 吗？该操作将同时删除所有关联的镜头和数据。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      try {
        isProcessing.value = true
        await projectStore.deleteProject(project.id)
        ElMessage.success('项目删除成功')
        emit('refresh')
        await loadProjects() // 重新加载项目列表
      } catch (error) {
        ElMessage.error('删除项目失败')
        console.error('删除项目失败', error)
      } finally {
        isProcessing.value = false
      }
    })
    .catch(() => {})
}

// 重置项目表单
const resetProjectForm = () => {
  projectForm.id = null
  projectForm.name = ''
  projectForm.code = ''
  projectForm.status = 'in_progress'
  projectForm.start_date = ''
  projectForm.end_date = ''
  projectForm.description = ''
  projectForm.department_ids = []
  
  // 重置表单验证
  if (projectFormRef.value) {
    projectFormRef.value.resetFields()
  }
}

// 提交项目表单
const submitProjectForm = async () => {
  if (!projectFormRef.value) return
  
  try {
    await projectFormRef.value.validate()
    
    isProcessing.value = true
    
    if (isEditMode.value) {
      // 更新项目
      const projectId = projectForm.id
      const projectData = { ...projectForm }
      delete projectData.id // 移除ID字段
      
      await projectStore.updateProject(projectId, projectData)
      ElMessage.success('项目更新成功')
    } else {
      // 创建项目
      await projectStore.createProject(projectForm)
      ElMessage.success('项目创建成功')
    }
    
    addProjectVisible.value = false
    resetProjectForm()
    emit('refresh')
    await loadProjects() // 重新加载项目列表
  } catch (error) {
    if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error(isEditMode.value ? '更新项目失败' : '创建项目失败')
    }
    console.error('提交项目表单失败', error)
  } finally {
    isProcessing.value = false
  }
}

// 初始化
onMounted(async () => {
  await loadProjects()
})

// 当对话框打开时，重新加载项目列表
watchEffect(() => {
  if (dialogVisible.value) {
    loadProjects()
  }
})
</script>

<style scoped>
.project-management {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.spacer {
  flex-grow: 1;
}

.departments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.department-tag {
  margin: 2px;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.date-info {
  font-size: 13px;
  color: #606266;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.project-name {
  font-weight: 500;
}
</style> 