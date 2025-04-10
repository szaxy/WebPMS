<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">荷和年动画项目管理平台</h1>
      <el-form 
        :model="loginForm" 
        :rules="rules"
        ref="loginFormRef"
        class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名" 
            prefix-icon="el-icon-user"
            @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="el-icon-lock"
            @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// 后续会导入授权服务
// import authService from '@/services/authService'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    // 模拟登录成功，后续会替换为实际登录API调用
    setTimeout(() => {
      localStorage.setItem('token', 'dummy-token')
      ElMessage.success('登录成功')
      router.push('/dashboard')
      loading.value = false
    }, 1000)
    
    // 实际登录逻辑会使用如下代码
    // const { data } = await authService.login(loginForm)
    // localStorage.setItem('token', data.access)
    // localStorage.setItem('refreshToken', data.refresh)
    // ElMessage.success('登录成功')
    // router.push('/dashboard')
    
  } catch (error) {
    loading.value = false
    console.error('登录失败:', error)
    ElMessage.error('用户名或密码错误')
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
  padding: 30px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: white;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
}
</style> 