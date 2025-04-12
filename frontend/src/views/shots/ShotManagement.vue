<template>
  <div class="shot-management">
    <!-- 页面顶部 -->
    <div class="shot-management-header">
      <h1 class="page-title">镜头管理</h1>
      <div class="filters">
        <!-- 项目选择 -->
        <el-select 
          v-model="selectedProject" 
          placeholder="选择项目" 
          clearable 
          @change="handleProjectChange"
          class="filter-item"
        >
          <el-option
            v-for="project in projects.filter(p => p && p.id)"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>

        <!-- 部门筛选 (仅对制片和管理员可见) -->
        <el-select
          v-if="canFilterByDepartment"
          v-model="filters.department"
          placeholder="选择部门"
          clearable
          @change="applyFilters"
          class="filter-item"
        >
          <el-option label="动画部门" value="DH" />
          <el-option label="解算部门" value="JS" />
          <el-option label="后期部门" value="HQ" />
        </el-select>

        <!-- 推进阶段筛选 -->
        <el-select
          v-model="filters.prom_stage"
          placeholder="推进阶段"
          clearable
          @change="applyFilters"
          class="filter-item"
        >
          <el-option label="Layout" value="LAY" />
          <el-option label="Block" value="BLK" />
          <el-option label="Animation" value="ANI" />
          <el-option label="Pass" value="PASS" />
        </el-select>

        <!-- 状态筛选 -->
        <el-select
          v-model="filters.status"
          placeholder="制作状态"
          clearable
          @change="applyFilters"
          class="filter-item"
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
          <el-option label="已删除或合并" value="deleted_merged" />
          <el-option label="暂停制作" value="suspended" />
          <el-option label="已完结" value="completed" />
        </el-select>

        <!-- 搜索框 -->
        <el-input
          v-model="searchQuery"
          placeholder="搜索镜头号..."
          clearable
          @input="applyFilters"
          class="filter-item search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <!-- 更多筛选按钮 -->
        <el-dropdown @command="handleAdvancedFilter" trigger="click">
          <el-button type="primary" plain>
            高级筛选
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="hasComments">有反馈的镜头</el-dropdown-item>
              <el-dropdown-item command="hasNotes">有备注的镜头</el-dropdown-item>
              <el-dropdown-item command="hasImportantNotes">有重要备注的镜头</el-dropdown-item>
              <el-dropdown-item command="overdueDeadline">已逾期镜头</el-dropdown-item>
              <el-dropdown-item command="upcomingDeadline">临近截止日期镜头</el-dropdown-item>
              <el-dropdown-item command="clearAll">清除所有筛选</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <div class="shot-management-content">
      <!-- 左侧导航与筛选 -->
      <div class="shot-sidebar">
        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <span>快速筛选</span>
            </div>
          </template>
          <el-menu @select="handleMenuSelect">
            <el-menu-item index="all">所有镜头</el-menu-item>
            <el-menu-item index="myShots">我负责的镜头</el-menu-item>
            <el-menu-item index="waiting">等待开始</el-menu-item>
            <el-menu-item index="in_progress">正在制作</el-menu-item>
            <el-menu-item index="review">待审核</el-menu-item>
            <el-menu-item index="completed">已完成</el-menu-item>
          </el-menu>
        </el-card>

        <el-card class="sidebar-card">
          <template #header>
            <div class="card-header">
              <span>列设置</span>
            </div>
          </template>
          <el-checkbox-group v-model="visibleColumns" @change="saveColumnSettings">
            <el-checkbox v-for="column in allColumns" :key="column.prop" :value="column.prop">
              {{ column.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-card>
      </div>

      <!-- 中间镜头列表区域 -->
      <div class="shot-list-container">
        <el-card>
          <template #header>
            <div class="list-header">
              <div class="list-title">
                镜头列表
                <el-tag v-if="filteredShots.length">{{ filteredShots.length }}个镜头</el-tag>
              </div>
              <div class="list-actions">
                <el-button-group>
                  <el-button @click="refreshShots" title="刷新">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                  <el-button @click="exportShots" title="导出">
                    <el-icon><Download /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
            </div>
            
            <!-- 批量操作工具栏 -->
            <div class="batch-actions" v-if="shotStore.selectedShotIds.length > 0">
              <div class="selected-info">
                已选择 <strong>{{ shotStore.selectedShotIds.length }}</strong> 个镜头
              </div>
              <div class="action-buttons">
                <el-button type="danger" @click="confirmBatchDelete" size="small">
                  <el-icon><Delete /></el-icon> 批量删除
                </el-button>
                <el-button type="info" @click="clearSelection" size="small">
                  <el-icon><Close /></el-icon> 取消选择
                </el-button>
              </div>
            </div>
          </template>

          <!-- 镜头表格 -->
          <el-table
            ref="shotTable"
            v-loading="loading"
            :data="filteredShots"
            @row-click="handleRowClick"
            :highlight-current-row="true"
            style="width: 100%"
            :max-height="tableHeight"
            stripe
            border
            @selection-change="handleSelectionChange"
          >
            <!-- 诊断信息 -->
            <template v-if="filteredShots.length === 0 && !loading" #empty>
              <div style="padding: 20px; text-align: left;">
                <h3>未找到镜头数据，请检查以下信息：</h3>
                <p><strong>当前项目:</strong> {{ selectedProject ? projects.find(p => p.id === selectedProject)?.name : '未选择项目' }}</p>
                <p><strong>当前用户角色:</strong> {{ authStore.user?.role || '未知' }}</p>
                <p><strong>当前用户部门:</strong> {{ userDepartment || '未知' }}</p>
                <p><strong>应用筛选:</strong> {{ JSON.stringify(filters) }}</p>
                <p><strong>搜索关键字:</strong> {{ searchQuery || '无' }}</p>
                <p><strong>项目总数:</strong> {{ projects.length }}</p>
                <div v-if="shotStore.error" class="error-message">
                  <strong>错误信息:</strong> {{ shotStore.error }}
                </div>
                <el-button type="primary" @click="refreshShots">刷新数据</el-button>
              </div>
            </template>
            
            <!-- 状态标记列 -->
            <el-table-column type="selection" width="55" />
            
            <el-table-column fixed width="40">
              <template #default="{ row }">
                <div class="status-indicators">
                  <el-tooltip v-if="row.has_comments" content="有反馈">
                    <div class="indicator comment-indicator"></div>
                  </el-tooltip>
                  <el-tooltip v-if="row.has_notes" content="有备注">
                    <div class="indicator note-indicator"></div>
                  </el-tooltip>
                  <el-tooltip v-if="row.has_important_notes" content="有重要备注">
                    <div class="indicator important-note-indicator"></div>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>

            <!-- 常规列 -->
            <el-table-column v-if="isColumnVisible('shot_code')" prop="shot_code" label="镜头号" fixed width="120" sortable />
            <el-table-column v-if="isColumnVisible('duration_frame')" prop="duration_frame" label="帧数" width="80" sortable />
            
            <el-table-column v-if="isColumnVisible('prom_stage')" label="推进阶段" width="120">
              <template #default="{ row }">
                <el-tag :type="getStageTagType(row.prom_stage)">
                  {{ row.prom_stage_display }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column v-if="isColumnVisible('status')" label="制作状态" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column v-if="isColumnVisible('artist')" label="制作者" width="120">
              <template #default="{ row }">
                <span>{{ row.artist_name || '-' }}</span>
              </template>
            </el-table-column>

            <el-table-column v-if="isColumnVisible('deadline')" label="截止日期" width="120" sortable>
              <template #default="{ row }">
                <span :class="getDeadlineClass(row)">
                  {{ formatDate(row.deadline) }}
                </span>
              </template>
            </el-table-column>

            <el-table-column v-if="isColumnVisible('last_submit_date')" label="最近提交" width="120" sortable>
              <template #default="{ row }">
                <span :class="getSubmitDateClass(row)">
                  {{ formatDate(row.last_submit_date) || '-' }}
                </span>
              </template>
            </el-table-column>

            <el-table-column v-if="isColumnVisible('department')" label="部门" width="100">
              <template #default="{ row }">
                <span>{{ row.department_display }}</span>
              </template>
            </el-table-column>

            <el-table-column v-if="isColumnVisible('description')" prop="description" label="描述" min-width="200" show-overflow-tooltip />

            <el-table-column v-if="isColumnVisible('updated_at')" label="更新时间" width="180" sortable>
              <template #default="{ row }">
                {{ formatDateTime(row.updated_at) }}
              </template>
            </el-table-column>

            <!-- 操作列 -->
            <el-table-column fixed="right" label="操作" width="180">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click.stop="viewShotDetails(scope.row)"
                >
                  详情
                </el-button>
                <el-button 
                  size="small" 
                  type="warning" 
                  @click.stop="editShot(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click.stop="confirmDeleteShot(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[20, 50, 100, 200]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="totalShotsCount"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </div>

      <!-- 右侧详情区域 -->
      <div v-if="selectedShot" class="shot-details-container">
        <ShotDetails 
          :shot="selectedShot" 
          @update="handleShotUpdate" 
          @close="selectedShot = null" 
        />
      </div>
    </div>
  </div>
  
  <!-- 镜头编辑对话框 -->
  <ShotEditDialog
    v-model:visible="editDialogVisible"
    :shot="currentEditShot"
    @saved="handleShotSaved"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Search, Refresh, Download, ArrowDown, Delete, Close } from '@element-plus/icons-vue'
import { useShotStore } from '@/stores/shotStore'
import { useProjectStore } from '@/stores/projectStore'
import { useAuthStore } from '@/stores/authStore'
import ShotDetails from '@/components/ShotDetails.vue'
import ShotEditDialog from '@/components/ShotEditDialog.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 店铺
const shotStore = useShotStore()
const projectStore = useProjectStore()
const authStore = useAuthStore()

// 数据
const loading = ref(false)
const selectedProject = ref(null)
const searchQuery = ref('')
const selectedShot = ref(null)
const shotTable = ref(null)
const tableHeight = ref(600)
const currentPage = ref(1)
const pageSize = ref(50)
const totalShotsCount = ref(0)
const editDialogVisible = ref(false)
const currentEditShot = ref(null)

// 用户角色
const canFilterByDepartment = computed(() => {
  return authStore.isAdmin || authStore.user?.role === 'producer'
})

// 获取用户部门
const userDepartment = computed(() => {
  return authStore.user?.department || null
})

// 筛选
const filters = reactive({
  department: canFilterByDepartment.value ? null : userDepartment.value,
  prom_stage: null,
  status: null,
  has_comments: null,
  has_notes: null,
  has_important_notes: null,
  artist: null,
  deadline_from: null,
  deadline_to: null
})

// 列设置
const allColumns = [
  { prop: 'shot_code', label: '镜头号' },
  { prop: 'duration_frame', label: '帧数' },
  { prop: 'prom_stage', label: '推进阶段' },
  { prop: 'status', label: '制作状态' },
  { prop: 'artist', label: '制作者' },
  { prop: 'deadline', label: '截止日期' },
  { prop: 'last_submit_date', label: '最近提交' },
  { prop: 'department', label: '部门' },
  { prop: 'description', label: '描述' },
  { prop: 'updated_at', label: '更新时间' }
]

// 初始可见列
const visibleColumns = ref([
  'shot_code', 'duration_frame', 'prom_stage', 'status', 
  'artist', 'deadline', 'last_submit_date'
])

// 加载项目列表
const projects = ref([])
const loadProjects = async () => {
  try {
    console.log('开始加载项目列表')
    const projectList = await projectStore.fetchProjects()
    console.log('原始项目数据:', projectList)
    
    // 确保项目列表是有效的数组，并且每个项目都有id
    if (Array.isArray(projectList)) {
      projects.value = projectList.filter(p => p && typeof p === 'object' && p.id)
      console.log('过滤后的项目列表:', projects.value)
    } else if (projectList && Array.isArray(projectList.results)) {
      // 处理分页响应
      projects.value = projectList.results.filter(p => p && typeof p === 'object' && p.id)
      console.log('从分页结果中过滤的项目列表:', projects.value)
    } else {
      console.error('项目数据格式不正确:', projectList)
      projects.value = []
    }
    
    // 如果有项目，默认选择第一个
    if (projects.value.length > 0 && !selectedProject.value) {
      console.log('自动选择第一个项目:', projects.value[0])
      selectedProject.value = projects.value[0].id
      await loadShots()
    } else if (projects.value.length === 0) {
      // 如果没有项目，显示提示
      console.warn('未找到任何项目')
      ElMessage({
        message: '暂无可用项目',
        type: 'info'
      })
    } else {
      console.log('使用当前选择的项目:', selectedProject.value)
    }
  } catch (error) {
    console.error('加载项目失败', error)
    if (error.response) {
      console.error('错误状态:', error.response.status)
      console.error('错误数据:', error.response.data)
    }
    ElMessage({
      message: '加载项目失败，请刷新页面重试',
      type: 'error'
    })
    projects.value = [] // 确保设置为空数组而不是undefined
  }
}

// 加载镜头列表
const loadShots = async () => {
  if (!selectedProject.value) {
    // 没有选择项目时，清空镜头列表
    shotStore.shots = []
    totalShotsCount.value = 0
    return
  }
  
  loading.value = true
  try {
    console.log('开始加载镜头，项目ID:', selectedProject.value)
    const params = {
      project: selectedProject.value,
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      search: searchQuery.value || undefined,
      ...filters
    }
    
    // 根据用户部门限制
    if (!canFilterByDepartment.value && userDepartment.value) {
      params.department = userDepartment.value
    }
    
    console.log('请求参数:', params)
    
    const response = await shotStore.fetchShots(params)
    console.log('API响应:', response)
    
    totalShotsCount.value = response?.count || 0
    
    if (shotStore.shots.length === 0) {
      console.log('没有找到镜头，用户角色:', authStore.user?.role, '用户部门:', userDepartment.value)
      // 使用导入的ElMessage
      ElMessage({ 
        message: '没有找到符合条件的镜头', 
        type: 'info' 
      })
    } else {
      console.log(`成功加载 ${shotStore.shots.length} 个镜头`)
    }
  } catch (error) {
    console.error('加载镜头失败', error)
    // 使用导入的ElMessage
    ElMessage({ 
      message: '加载镜头失败，请检查网络连接或刷新页面', 
      type: 'error' 
    })
    shotStore.shots = [] // 确保是空数组
    totalShotsCount.value = 0
  } finally {
    loading.value = false
  }
}

// 过滤后的镜头列表
const filteredShots = computed(() => {
  return shotStore.shots
})

// 处理项目变更
const handleProjectChange = async () => {
  currentPage.value = 1
  await loadShots()
}

// 应用筛选
const applyFilters = async () => {
  currentPage.value = 1
  await loadShots()
}

// 刷新镜头列表
const refreshShots = async () => {
  await loadShots()
}

// 导出镜头列表
const exportShots = () => {
  // TODO: 实现导出功能
  ElMessage({
    message: '导出功能开发中...',
    type: 'info'
  })
}

// 表格行选择变化
const handleSelectionChange = (selection) => {
  shotStore.selectAllShots(false) // 先清空
  selection.forEach(shot => {
    shotStore.selectShot(shot.id)
  })
}

// 处理行点击
const handleRowClick = (row, column) => {
  // 如果点击的是选择框列，不执行任何操作
  if (column.type === 'selection') return
  
  // 否则查看镜头详情
  viewShotDetails(row)
}

// 查看镜头详情
const viewShotDetails = (shot) => {
  selectedShot.value = shot
}

// 编辑镜头
const editShot = (shot) => {
  currentEditShot.value = shot
  editDialogVisible.value = true
}

// 处理镜头更新
const handleShotUpdate = (updatedShot) => {
  // 刷新当前选中的镜头数据
  if (selectedShot.value && selectedShot.value.id === updatedShot.id) {
    selectedShot.value = updatedShot
  }
  
  // 刷新镜头列表中的数据
  const index = shotStore.shots.findIndex(s => s.id === updatedShot.id)
  if (index !== -1) {
    shotStore.shots[index] = updatedShot
  }
}

// 处理高级筛选
const handleAdvancedFilter = (command) => {
  switch (command) {
    case 'hasComments':
      filters.has_comments = true
      filters.has_notes = null
      filters.has_important_notes = null
      break
    case 'hasNotes':
      filters.has_comments = null
      filters.has_notes = true
      filters.has_important_notes = null
      break
    case 'hasImportantNotes':
      filters.has_comments = null
      filters.has_notes = null
      filters.has_important_notes = true
      break
    case 'overdueDeadline':
      const today = new Date()
      filters.deadline_to = today.toISOString().split('T')[0]
      break
    case 'upcomingDeadline':
      const now = new Date()
      const nextWeek = new Date(now)
      nextWeek.setDate(now.getDate() + 7)
      
      filters.deadline_from = now.toISOString().split('T')[0]
      filters.deadline_to = nextWeek.toISOString().split('T')[0]
      break
    case 'clearAll':
      Object.keys(filters).forEach(key => {
        filters[key] = null
      })
      searchQuery.value = ''
      break
  }
  
  applyFilters()
}

// 处理菜单选择
const handleMenuSelect = (key) => {
  // 清除之前的筛选
  Object.keys(filters).forEach(k => {
    filters[k] = null
  })
  
  switch (key) {
    case 'all':
      // 清除所有筛选
      break
    case 'myShots':
      filters.artist = authStore.user?.id
      break
    case 'waiting':
      filters.status = 'waiting'
      break
    case 'in_progress':
      filters.status = 'in_progress'
      break
    case 'review':
      filters.status = 'submit_review'
      break
    case 'completed':
      filters.status = 'completed'
      break
  }
  
  applyFilters()
}

// 处理分页
const handleSizeChange = async (size) => {
  pageSize.value = size
  await loadShots()
}

const handleCurrentChange = async (page) => {
  currentPage.value = page
  await loadShots()
}

// 列可见性
const isColumnVisible = (prop) => {
  return visibleColumns.value.includes(prop)
}

// 保存列设置
const saveColumnSettings = () => {
  localStorage.setItem('shotColumns', JSON.stringify(visibleColumns.value))
}

// 加载列设置
const loadColumnSettings = () => {
  const savedColumns = localStorage.getItem('shotColumns')
  if (savedColumns) {
    visibleColumns.value = JSON.parse(savedColumns)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-CN').format(date)
}

// 格式化日期时间
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return '-'
  const date = new Date(dateTimeString)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

// 获取截止日期样式
const getDeadlineClass = (shot) => {
  if (!shot.deadline) return ''
  
  const today = new Date()
  const deadline = new Date(shot.deadline)
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return 'text-danger' // 已逾期
  } else if (diffDays <= 7) {
    return 'text-warning' // 临近
  }
  return ''
}

// 获取提交日期样式
const getSubmitDateClass = (shot) => {
  if (!shot.deadline || !shot.last_submit_date) return ''
  
  const today = new Date()
  const deadline = new Date(shot.deadline)
  const diffDays = Math.ceil((deadline - today) / (1000 * 60 * 60 * 24))
  
  if (shot.last_submit_date) {
    if (diffDays < 0) {
      return 'text-warning' // 已提交但逾期
    }
    return ''
  }
  
  if (diffDays < 0) {
    return 'text-danger' // 未提交且逾期
  }
  return ''
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const statusMap = {
    'waiting': 'info',
    'in_progress': 'primary',
    'submit_review': 'warning',
    'revising': 'danger',
    'internal_approved': 'success',
    'client_review': 'warning',
    'client_rejected': 'danger',
    'client_approved': 'success',
    'client_revision': 'danger',
    'deleted_merged': 'info',
    'suspended': 'info',
    'completed': 'success'
  }
  
  return statusMap[status] || 'info'
}

// 获取阶段标签类型
const getStageTagType = (stage) => {
  const stageMap = {
    'LAY': 'info',
    'BLK': 'warning',
    'ANI': 'primary',
    'PASS': 'success'
  }
  
  return stageMap[stage] || 'info'
}

// 调整表格高度
const adjustTableHeight = () => {
  nextTick(() => {
    const windowHeight = window.innerHeight
    const headerHeight = 120 // 预估头部高度
    const paginationHeight = 50 // 预估分页高度
    const padding = 40 // 边距

    tableHeight.value = windowHeight - headerHeight - paginationHeight - padding
  })
}

// 监听窗口大小变化
window.addEventListener('resize', adjustTableHeight)

// 生命周期钩子
onMounted(async () => {
  console.log('组件挂载，当前用户信息:', authStore.user)
  
  // 如果用户信息未加载，先等待加载完成
  if (!authStore.user && authStore.token) {
    console.log('尝试加载用户信息...')
    try {
      await authStore.fetchUserInfo()
      console.log('用户信息加载成功:', authStore.user)
    } catch (error) {
      console.error('加载用户信息失败:', error)
      ElMessage({
        message: '获取用户信息失败，可能影响数据访问权限',
        type: 'warning'
      })
    }
  }
  
  loadColumnSettings()
  await loadProjects()
  adjustTableHeight()
  
  // 监听选中变化
 // shotTable.value?.store.states.selection.value = shotStore.selectedShots
  
  // 监听选中变化
  if (shotTable.value && shotTable.value.store && shotTable.value.store.states) {
    shotTable.value.store.states.selection.value = shotStore.selectedShots
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', adjustTableHeight)
})

// 处理镜头保存
const handleShotSaved = async (updatedShot) => {
  ElMessage.success('镜头保存成功')
  await refreshShots()
  currentEditShot.value = null
}

// 确认删除单个镜头
const confirmDeleteShot = (shot) => {
  ElMessageBox.confirm(
    `确定要删除镜头 "${shot.shot_code}" 吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const success = await shotStore.deleteShot(shot.id)
      if (success) {
        ElMessage.success('镜头删除成功')
        await refreshShots()
      } else {
        ElMessage.error(shotStore.error || '删除失败')
      }
    } catch (error) {
      console.error('删除镜头失败', error)
      ElMessage.error('删除镜头失败，请重试')
    }
  }).catch(() => {
    // 用户取消删除，不执行任何操作
  })
}

// 确认批量删除
const confirmBatchDelete = () => {
  if (shotStore.selectedShotIds.length === 0) {
    ElMessage.warning('请选择要删除的镜头')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${shotStore.selectedShotIds.length} 个镜头吗？此操作不可恢复。`,
    '批量删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      loading.value = true
      
      // 逐个删除，提高成功率
      let successCount = 0
      let failCount = 0
      const totalCount = shotStore.selectedShotIds.length
      
      // 复制一份ID列表以避免在循环中修改
      const idsToDelete = [...shotStore.selectedShotIds]
      
      console.log(`开始批量删除 ${idsToDelete.length} 个镜头...`)
      for (const id of idsToDelete) {
        try {
          const success = await shotStore.deleteShot(id)
          if (success) {
            successCount++
          } else {
            failCount++
          }
        } catch (err) {
          console.error(`删除镜头 ${id} 时发生错误:`, err)
          failCount++
        }
      }
      
      // 汇总结果
      if (successCount > 0) {
        ElMessage.success(`成功删除 ${successCount} 个镜头`)
      }
      
      if (failCount > 0) {
        ElMessage.warning(`有 ${failCount} 个镜头删除失败`)
      }
      
      // 清空选择
      shotStore.selectAllShots(false)
      
      // 刷新列表
      await refreshShots()
    } catch (error) {
      console.error('批量删除过程中发生错误:', error)
      ElMessage.error('批量删除过程中发生错误，请检查控制台日志')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消删除，不执行任何操作
  })
}

// 清除选择
const clearSelection = () => {
  shotStore.selectAllShots(false)
  if (shotTable.value) {
    shotTable.value.clearSelection()
  }
}
</script>

<style scoped>
.shot-management {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.shot-management-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  min-width: 120px;
}

.search-input {
  width: 200px;
}

.shot-management-content {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 0 16px 16px;
  overflow: hidden;
}

.shot-sidebar {
  width: 250px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sidebar-card {
  height: fit-content;
}

.shot-list-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.shot-details-container {
  width: 400px;
  overflow-y: auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicators {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.comment-indicator {
  background-color: #409EFF; /* 蓝色 */
}

.note-indicator {
  background-color: #E6A23C; /* 橙色 */
}

.important-note-indicator {
  background-color: #F56C6C; /* 红色 */
}

.text-danger {
  color: #F56C6C;
}

.text-warning {
  color: #E6A23C;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #f0f0f0;
}

.selected-info {
  font-size: 12px;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
</style> 