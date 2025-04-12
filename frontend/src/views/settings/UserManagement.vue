<template>
  <div class="user-management-container">
    <el-card class="user-management-card">
      <template #header>
        <div class="card-header">
          <h3>用户管理</h3>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="goToDashboard">返回主页</el-button>
            <el-button type="success" size="small" @click="refreshData">刷新</el-button>
          </div>
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
              <el-table-column prop="device_code" label="设备代号" min-width="180" />
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
              placeholder="搜索用户名或设备代号"
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
              <el-option label="管理员" value="admin" />
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
          
          <div v-if="loadingError" class="error-message">
            <el-alert
              type="error"
              :title="loadingError"
              :closable="false"
              show-icon
            />
            <el-button type="primary" @click="refreshData" class="retry-button">重试</el-button>
          </div>
          
          <div v-else class="table-container">
            <el-table
              v-loading="authStore.loading"
              :data="filteredUsers"
              style="width: 100%"
              border
              stripe>
              <el-table-column prop="username" label="用户名" min-width="120" />
              <el-table-column prop="device_code" label="设备代号" min-width="180" />
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
                  <el-tag v-else-if="scope.row.department === 'admin'" type="info">管理员</el-tag>
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
              <el-table-column label="操作" width="220">
                <template #default="scope">
                  <el-button 
                    type="primary" 
                    size="small"
                    @click="viewUserDetails(scope.row)">
                    详情
                  </el-button>
                  <el-button 
                    type="warning" 
                    size="small"
                    @click="editUser(scope.row)">
                    编辑
                  </el-button>
                  <el-button 
                    type="danger" 
                    size="small"
                    @click="confirmDeleteUser(scope.row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="filteredUsers.length === 0 && !authStore.loading" class="empty-data">
              <el-empty description="没有找到符合条件的用户" />
            </div>
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
          <span class="label">设备代号：</span>
          <span class="value">{{ selectedUser.device_code }}</span>
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
    
    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="userEditVisible"
      title="编辑用户"
      width="500px">
      <div v-if="editingUser" class="user-edit">
        <el-form :model="editingUser" :rules="userEditRules" ref="userEditFormRef" label-width="100px">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="editingUser.username" disabled></el-input>
          </el-form-item>
          <el-form-item label="设备代号" prop="device_code">
            <el-input v-model="editingUser.device_code"></el-input>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="editingUser.role" style="width: 100%">
              <el-option label="系统管理员" value="admin" />
              <el-option label="主管" value="supervisor" />
              <el-option label="带片" value="leader" />
              <el-option label="制片" value="producer" />
              <el-option label="艺术家" value="artist" />
            </el-select>
          </el-form-item>
          <el-form-item label="部门" prop="department">
            <el-select v-model="editingUser.department" style="width: 100%">
              <el-option label="动画" value="animation" />
              <el-option label="后期" value="post" />
              <el-option label="解算" value="fx" />
              <el-option label="制片" value="producer" />
              <el-option label="模型" value="model" />
              <el-option label="管理员" value="admin" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="registration_status">
            <el-select v-model="editingUser.registration_status" style="width: 100%">
              <el-option label="已批准" value="approved" />
              <el-option label="待审核" value="pending" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注" prop="registration_notes">
            <el-input 
              v-model="editingUser.registration_notes" 
              type="textarea" 
              rows="3"
              placeholder="用户备注" />
          </el-form-item>
        </el-form>
        <div class="dialog-footer">
          <el-button @click="userEditVisible = false">取消</el-button>
          <el-button type="primary" @click="saveUserEdit" :loading="authStore.loading">保存</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref('pending')
const userDetailVisible = ref(false)
const selectedUser = ref(null)
const searchTimeout = ref(null)
const loadingError = ref(null)
const userEditVisible = ref(false)
const editingUser = ref(null)
const userEditFormRef = ref(null)

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
  if (!authStore.users || !Array.isArray(authStore.users)) return []
  
  console.log('过滤用户数据，总数:', authStore.users.length)
  let result = [...authStore.users]
  
  // 搜索过滤
  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    result = result.filter(user => 
      user.username.toLowerCase().includes(searchLower) || 
      (user.device_code && user.device_code.toLowerCase().includes(searchLower))
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
  
  console.log('过滤后用户数:', result.length)
  return result
})

// 加载数据
const loadData = async () => {
  loadingError.value = null
  
  try {
    if (activeTab.value === 'pending') {
      console.log('加载待审核用户数据')
      await authStore.fetchPendingUsers()
      console.log('待审核用户数据加载完成:', authStore.pendingUsers?.length || 0)
    } else if (activeTab.value === 'all') {
      console.log('开始加载所有用户数据...')
      const result = await authStore.fetchUsers()
      console.log('所有用户数据加载结果:', 
        result?.success ? '成功' : '失败',
        '用户数:', authStore.users?.length || 0
      )
      
      if (!result || !result.success) {
        loadingError.value = result?.error || authStore.error || '加载用户列表失败，请重试'
        console.error('加载用户列表失败:', loadingError.value)
      }
    }
  } catch (err) {
    console.error('加载数据出错:', err)
    loadingError.value = err.message || '加载数据时出错，请重试'
  }
}

// 刷新数据
const refreshData = async () => {
  await loadData()
  if (!loadingError.value) {
    ElMessage.success('数据已刷新')
  }
}

// 切换标签页
const handleTabClick = () => {
  loadData()
}

// 前往主页
const goToDashboard = () => {
  router.push('/dashboard')
}

// 搜索处理（防抖）
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = setTimeout(() => {
    // 简单的前端过滤，不需要额外操作
    console.log('执行搜索过滤')
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
    
    console.log('提交用户审核:', user.id, status)
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

// 用户编辑表单规则
const userEditRules = {
  device_code: [
    { pattern: /^[A-Z0-9]{5,10}$/, message: '设备代号格式不正确，应为5-10位大写字母和数字', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  department: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  registration_status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 编辑用户
const editUser = (user) => {
  editingUser.value = { ...user }
  userEditVisible.value = true
}

// 保存用户编辑
const saveUserEdit = async () => {
  if (!userEditFormRef.value) return
  
  try {
    await userEditFormRef.value.validate()
    
    // 处理设备代号大写
    if (editingUser.value.device_code) {
      editingUser.value.device_code = editingUser.value.device_code.toUpperCase()
    }
    
    const result = await authStore.updateUser(editingUser.value.id, editingUser.value)
    
    if (result.success) {
      ElMessage.success('用户信息更新成功')
      userEditVisible.value = false
      
      // 刷新数据
      await loadData()
    } else {
      ElMessage.error(result.error || '更新用户信息失败')
    }
  } catch (err) {
    console.error('更新用户信息出错:', err)
    ElMessage.error('表单验证失败，请检查输入')
  }
}

// 确认删除用户
const confirmDeleteUser = (user) => {
  ElMessageBox.confirm(
    `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`,
    '删除用户',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      const result = await authStore.deleteUser(user.id)
      if (result.success) {
        ElMessage.success(`已删除用户 "${user.username}"`)
        await loadData()
      } else {
        ElMessage.error(result.error || '删除用户失败')
      }
    })
    .catch(() => {
      // 用户取消删除，无需操作
    })
}

// 初始化监听组件错误
watch(() => authStore.error, (newError) => {
  if (newError) {
    loadingError.value = newError
  }
})

// 页面加载时获取数据
onMounted(() => {
  console.log('用户管理组件挂载，初始化加载数据')
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

.header-actions {
  display: flex;
  gap: 10px;
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

.error-message {
  margin: 20px 0;
  text-align: center;
}

.retry-button {
  margin-top: 10px;
}

.dialog-footer {
  margin-top: 20px;
  text-align: right;
}
</style> 