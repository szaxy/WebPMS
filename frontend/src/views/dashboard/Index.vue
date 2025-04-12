<template>
  <div class="dashboard">
    <el-container>
      <el-aside width="200px">
        <el-menu
          default-active="dashboard"
          class="sidebar-menu"
          router>
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/shots">
            <el-icon><VideoCameraFilled /></el-icon>
            <span>镜头管理</span>
          </el-menu-item>
          <el-menu-item index="/comments">
            <el-icon><ChatLineRound /></el-icon>
            <span>反馈系统</span>
          </el-menu-item>
          
          <el-sub-menu index="settings" v-if="authStore.isAdmin">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>管理设置</span>
            </template>
            <el-menu-item index="/settings/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/settings">
            <el-icon><Tools /></el-icon>
            <span>个人设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-wrapper">
            <h2>荷和年动画项目管理平台</h2>
            <div class="user-info">
              <span v-if="authStore.user">
                {{ authStore.user.username }} 
                <el-tag v-if="authStore.isAdmin" type="danger" size="small">管理员</el-tag>
                <el-tag v-else-if="authStore.isSupervisor" type="warning" size="small">主管</el-tag>
                <el-tag v-else-if="authStore.isLeader" type="success" size="small">带片</el-tag>
                <el-tag v-else-if="authStore.user.role === 'producer'" type="info" size="small">制片</el-tag>
                <el-tag v-else type="primary" size="small">艺术家</el-tag>
              </span>
              <el-dropdown trigger="click">
                <el-button type="primary" size="small">
                  <el-icon><User /></el-icon>
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        <el-main>
          <div class="dashboard-content">
            <el-card class="welcome-card">
              <h2>欢迎使用荷和年动画项目管理平台</h2>
              <p>这是一个完整的动画制作项目管理系统，集成了项目管理、镜头跟踪和反馈系统。</p>
              
              <div v-if="authStore.isAdmin" class="admin-actions">
                <h3>管理员快捷操作</h3>
                <el-button 
                  type="primary" 
                  @click="router.push('/settings/users')" 
                  :loading="pendingCount === null">
                  用户管理
                  <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge" />
                </el-button>
              </div>
            </el-card>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="stat-card">
                  <template #header>
                    <div class="card-header">
                      <span>进行中的项目</span>
                    </div>
                  </template>
                  <div class="stat-value">5</div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="stat-card">
                  <template #header>
                    <div class="card-header">
                      <span>总镜头数</span>
                    </div>
                  </template>
                  <div class="stat-value">128</div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="stat-card">
                  <template #header>
                    <div class="card-header">
                      <span>待处理反馈</span>
                    </div>
                  </template>
                  <div class="stat-value">12</div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/authStore'
import { 
  HomeFilled, 
  VideoCameraFilled, 
  ChatLineRound, 
  Setting, 
  Tools, 
  User,
  ArrowDown
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const pendingCount = ref(null)

const handleLogout = () => {
  authStore.logout()
  ElMessage.success('退出登录成功')
  router.push('/login')
}

// 获取待审核用户数量
const fetchPendingCount = async () => {
  if (authStore.isAdmin) {
    await authStore.fetchPendingUsers()
    pendingCount.value = authStore.pendingUsers?.length || 0
  }
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    errors.value = []
    
    if (!authStore.user) {
      await authStore.fetchCurrentUser()
    }
    
    // 如果用户是管理员，加载待审核用户
    if (authStore.isAdmin) {
      try {
        await authStore.fetchPendingUsers()
        pendingUsersData.value = authStore.pendingUsers
      } catch (error) {
        console.error('加载待审核用户失败:', error)
        errors.value.push('加载待审核用户失败')
      }
    }
    
    // 加载项目统计数据
    await loadProjectStats()
    
    // 加载最近镜头活动
    await loadRecentShotActivities()
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
    errors.value.push('加载数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // 如果没有用户信息，获取用户信息
  if (!authStore.user) {
    await authStore.fetchCurrentUser()
  }
  
  // 如果是管理员，获取待审核用户数量
  if (authStore.isAdmin) {
    fetchPendingCount()
  }
})
</script>

<style scoped>
.dashboard {
  height: 100%;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: white;
}

.el-header {
  background-color: white;
  color: #333;
  line-height: 60px;
  border-bottom: 1px solid #e6e6e6;
}

.header-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sidebar-menu {
  height: 100%;
  background-color: #304156;
}

.dashboard-content {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-card h2 {
  margin-bottom: 10px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.admin-actions {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.admin-actions h3 {
  margin-bottom: 10px;
}

.badge {
  margin-top: -2px;
  margin-left: 8px;
}
</style> 