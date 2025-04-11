<template>
  <div class="user-management-container">
    <el-card class="user-management-card">
      <template #header>
        <div class="card-header">
          <h3>用户管理</h3>
          <el-button type="primary" size="small" @click="refreshData">刷新</el-button>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="待审核用户" name="pending">
          <div class="table-container">
            <el-table
              v-loading="authStore.loading"
              :data="pendingUsers"
              style="width: 100%"
              border
              stripe>
              <el-table-column prop="username" label="用户名" min-width="120" />
              <el-table-column prop="email" label="邮箱" min-width="180" />
              <el-table-column prop="role" label="申请角色" min-width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.role === 'admin'" type="danger">系统管理员</el-tag>
                  <el-tag v-else-if="scope.row.role === 'supervisor'" type="warning">主管</el-tag>
                  <el-tag v-else-if="scope.row.role === 'leader'" type="success">带片</el-tag>
                  <el-tag v-else-if="scope.row.role === 'producer'" type="info">制片</el-tag>
                  <el-tag v-else-if="scope.row.role === 'artist'" type="primary">艺术家</el-tag>
                  <span v-else>{{ scope.row.role }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="department" label="部门" min-width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.department === 'animation'" type="primary">动画</el-tag>
                  <el-tag v-else-if="scope.row.department === 'post'" type="success">后期</el-tag>
                  <el-tag v-else-if="scope.row.department === 'fx'" type="warning">解算</el-tag>
                  <el-tag v-else-if="scope.row.department === 'producer'" type="info">制片</el-tag>
                  <el-tag v-else-if="scope.row.department === 'model'" type="danger">模型</el-tag>
                  <span v-else>{{ scope.row.department }}</span>
                </template>
              </el-table-column>
              <el-table-column label="审核操作" width="220">
                <template #default="scope">
                  <div class="approval-actions">
                    <el-button 
                      type="success" 
                      size="small"
                      @click="approveUser(scope.row, 'approved')">
                      批准
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small"
                      @click="approveUser(scope.row, 'rejected')">
                      拒绝
                    </el-button>
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="viewUserDetails(scope.row)">
                      详情
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="pendingUsers.length === 0 && !authStore.loading" class="empty-data">
              <el-empty description="暂无待审核用户" />
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="所有用户" name="all">
          <div class="filters">
            <el-input
              v-model="filters.search"
              placeholder="搜索用户名或邮箱"
              clearable
              class="filter-item"
              @input="handleSearch"
            />
            <el-select
              v-model="filters.role"
              placeholder="角色筛选"
              clearable
              class="filter-item"
              @change="handleSearch"
            >
              <el-option label="系统管理员" value="admin" />
              <el-option label="主管" value="supervisor" />
              <el-option label="带片" value="leader" />
              <el-option label="制片" value="producer" />
              <el-option label="艺术家" value="artist" />
            </el-select>
            <el-select
              v-model="filters.department"
              placeholder="部门筛选"
              clearable
              class="filter-item"
              @change="handleSearch"
            >
              <el-option label="动画" value="animation" />
              <el-option label="后期" value="post" />
              <el-option label="解算" value="fx" />
              <el-option label="制片" value="producer" />
              <el-option label="模型" value="model" />
            </el-select>
            <el-select
              v-model="filters.status"
              placeholder="状态筛选"
              clearable
              class="filter-item"
              @change="handleSearch"
            >
              <el-option label="已批准" value="approved" />
              <el-option label="待审核" value="pending" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </div>
          
          <div class="table-container">
            <el-table
              v-loading="authStore.loading"
              :data="filteredUsers"
              style="width: 100%"
              border
              stripe>
              <el-table-column prop="username" label="用户名" min-width="120" />
              <el-table-column prop="email" label="邮箱" min-width="180" />
              <el-table-column prop="role" label="角色" min-width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.role === 'admin'" type="danger">系统管理员</el-tag>
                  <el-tag v-else-if="scope.row.role === 'supervisor'" type="warning">主管</el-tag>
                  <el-tag v-else-if="scope.row.role === 'leader'" type="success">带片</el-tag>
                  <el-tag v-else-if="scope.row.role === 'producer'" type="info">制片</el-tag>
                  <el-tag v-else-if="scope.row.role === 'artist'" type="primary">艺术家</el-tag>
                  <span v-else>{{ scope.row.role }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="department" label="部门" min-width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.department === 'animation'" type="primary">动画</el-tag>
                  <el-tag v-else-if="scope.row.department === 'post'" type="success">后期</el-tag>
                  <el-tag v-else-if="scope.row.department === 'fx'" type="warning">解算</el-tag>
                  <el-tag v-else-if="scope.row.department === 'producer'" type="info">制片</el-tag>
                  <el-tag v-else-if="scope.row.department === 'model'" type="danger">模型</el-tag>
                  <span v-else>{{ scope.row.department }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="registration_status" label="状态" min-width="100">
                <template #default="scope">
                  <el-tag v-if="scope.row.registration_status === 'approved'" type="success">已批准</el-tag>
                  <el-tag v-else-if="scope.row.registration_status === 'pending'" type="warning">待审核</el-tag>
                  <el-tag v-else-if="scope.row.registration_status === 'rejected'" type="danger">已拒绝</el-tag>
                  <span v-else>{{ scope.row.registration_status }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="viewUserDetails(scope.row)">
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 用户详情对话框 -->
    <el-dialog
      v-model="userDetailVisible"
      title="用户详情"
      width="500px">
      <div v-if="selectedUser" class="user-detail">
        <div class="user-detail-item">
          <span class="label">用户名：</span>
          <span class="value">{{ selectedUser.username }}</span>
        </div>
        <div class="user-detail-item">
          <span class="label">邮箱：</span>
          <span class="value">{{ selectedUser.email }}</span>
        </div>
        <div class="user-detail-item">
          <span class="label">角色：</span>
          <span class="value">
            <el-tag v-if="selectedUser.role === 'admin'" type="danger">系统管理员</el-tag>
            <el-tag v-else-if="selectedUser.role === 'supervisor'" type="warning">主管</el-tag>
            <el-tag v-else-if="selectedUser.role === 'leader'" type="success">带片</el-tag>
            <el-tag v-else-if="selectedUser.role === 'producer'" type="info">制片</el-tag>
            <el-tag v-else-if="selectedUser.role === 'artist'" type="primary">艺术家</el-tag>
            <span v-else>{{ selectedUser.role }}</span>
          </span>
        </div>
        <div class="user-detail-item">
          <span class="label">部门：</span>
          <span class="value">
            <el-tag v-if="selectedUser.department === 'animation'" type="primary">动画</el-tag>
            <el-tag v-else-if="selectedUser.department === 'post'" type="success">后期</el-tag>
            <el-tag v-else-if="selectedUser.department === 'fx'" type="warning">解算</el-tag>
            <el-tag v-else-if="selectedUser.department === 'producer'" type="info">制片</el-tag>
            <el-tag v-else-if="selectedUser.department === 'model'" type="danger">模型</el-tag>
            <span v-else>{{ selectedUser.department }}</span>
          </span>
        </div>
        <div class="user-detail-item">
          <span class="label">注册状态：</span>
          <span class="value">
            <el-tag v-if="selectedUser.registration_status === 'approved'" type="success">已批准</el-tag>
            <el-tag v-else-if="selectedUser.registration_status === 'pending'" type="warning">待审核</el-tag>
            <el-tag v-else-if="selectedUser.registration_status === 'rejected'" type="danger">已拒绝</el-tag>
            <span v-else>{{ selectedUser.registration_status }}</span>
          </span>
        </div>
        <div class="user-detail-item">
          <span class="label">注册备注：</span>
          <div class="value note-box">
            {{ selectedUser.registration_notes || '无' }}
          </div>
        </div>
        
        <div v-if="selectedUser.registration_status === 'pending'" class="approval-actions mt-20">
          <el-form :model="approvalForm">
            <el-form-item label="审核备注">
              <el-input 
                v-model="approvalForm.registration_notes" 
                type="textarea" 
                rows="3"
                placeholder="添加审核备注（可选）" />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="success" 
                @click="approveUser(selectedUser, 'approved')">
                批准
              </el-button>
              <el-button 
                type="danger" 
                @click="approveUser(selectedUser, 'rejected')">
                拒绝
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const activeTab = ref('pending')
const userDetailVisible = ref(false)
const selectedUser = ref(null)
const searchTimeout = ref(null)

const approvalForm = reactive({
  registration_notes: ''
})

const filters = reactive({
  search: '',
  role: '',
  department: '',
  status: ''
})

// 计算属性：待审核用户
const pendingUsers = computed(() => {
  return authStore.pendingUsers || []
})

// 计算属性：过滤后的所有用户
const filteredUsers = computed(() => {
  let result = authStore.users || []
  
  // 搜索过滤
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(searchLower) || 
      (user.email && user.email.toLowerCase().includes(searchLower))
    )
  }
  
  // 角色过滤
  if (filters.role) {
    result = result.filter(user => user.role === filters.role)
  }
  
  // 部门过滤
  if (filters.department) {
    result = result.filter(user => user.department === filters.department)
  }
  
  // 状态过滤
  if (filters.status) {
    result = result.filter(user => user.registration_status === filters.status)
  }
  
  return result
})

// 加载数据
const loadData = async () => {
  if (activeTab.value === 'pending') {
    await authStore.fetchPendingUsers()
  } else {
    await authStore.fetchUsers()
  }
}

// 刷新数据
const refreshData = async () => {
  await loadData()
  ElMessage.success('数据已刷新')
}

// 切换标签页
const handleTabClick = () => {
  loadData()
}

// 搜索处理（防抖）
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(() => {
    // 这里可以添加远程搜索逻辑，目前使用本地过滤
  }, 300)
}

// 查看用户详情
const viewUserDetails = (user) => {
  selectedUser.value = user
  approvalForm.registration_notes = user.registration_notes || ''
  userDetailVisible.value = true
}

// 审核用户
const approveUser = async (user, status) => {
  try {
    const actionText = status === 'approved' ? '批准' : '拒绝'
    
    await ElMessageBox.confirm(
      `确定要${actionText}用户 "${user.username}" 的注册申请吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: status === 'approved' ? 'success' : 'warning'
      }
    )
    
    const result = await authStore.approveUser(user.id, {
      registration_status: status,
      registration_notes: approvalForm.registration_notes
    })
    
    if (result.success) {
      ElMessage.success(`已${actionText}用户 "${user.username}" 的注册申请`)
      userDetailVisible.value = false
      
      // 刷新数据
      loadData()
    } else {
      ElMessage.error(result.error || `${actionText}操作失败`)
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('审核用户出错:', err)
      ElMessage.error('操作失败，请重试')
    }
  }
}

// 页面加载时获取数据
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.user-management-container {
  padding: 20px;
}

.user-management-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-container {
  margin-top: 20px;
}

.empty-data {
  margin: 40px 0;
  text-align: center;
}

.approval-actions {
  display: flex;
  gap: 5px;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-item {
  width: 200px;
}

.user-detail-item {
  margin-bottom: 15px;
  display: flex;
}

.user-detail-item .label {
  font-weight: bold;
  width: 100px;
  margin-right: 10px;
}

.user-detail-item .value {
  flex: 1;
}

.note-box {
  background-color: #f8f8f8;
  padding: 10px;
  border-radius: 4px;
  min-height: 40px;
  white-space: pre-wrap;
}

.mt-20 {
  margin-top: 20px;
}
</style> 