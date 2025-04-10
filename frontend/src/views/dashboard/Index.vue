<template>
  <div class="dashboard">
    <el-container>
      <el-aside width="200px">
        <el-menu
          default-active="dashboard"
          class="sidebar-menu"
          router>
          <el-menu-item index="/dashboard">
            <i class="el-icon-s-home"></i>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/shots">
            <i class="el-icon-film"></i>
            <span>镜头管理</span>
          </el-menu-item>
          <el-menu-item index="/comments">
            <i class="el-icon-chat-line-round"></i>
            <span>反馈系统</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <i class="el-icon-setting"></i>
            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header>
          <div class="header-wrapper">
            <h2>荷和年动画项目管理平台</h2>
            <div class="user-info">
              <span>管理员</span>
              <el-dropdown trigger="click">
                <span class="el-dropdown-link">
                  操作<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('token')
  ElMessage.success('退出登录成功')
  router.push('/login')
}
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
}

.user-info span {
  margin-right: 10px;
}

.el-dropdown-link {
  cursor: pointer;
  color: #409EFF;
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
</style> 