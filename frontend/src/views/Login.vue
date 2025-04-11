<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">荷和年动画项目管理平台</h1>
      
      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form 
            :model="loginForm" 
            :rules="loginRules"
            ref="loginFormRef"
            class="login-form">
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="用户名" 
                prefix-icon="User"
                @keyup.enter="handleLogin" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="密码" 
                prefix-icon="Lock"
                @keyup.enter="handleLogin" />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                :loading="authStore.loading" 
                class="login-button" 
                @click="handleLogin">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="注册" name="register">
          <el-form 
            :model="registerForm" 
            :rules="registerRules"
            ref="registerFormRef"
            class="register-form">
            <el-form-item prop="username">
              <el-input 
                v-model="registerForm.username" 
                placeholder="用户名" 
                prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="email">
              <el-input 
                v-model="registerForm.email" 
                placeholder="邮箱" 
                prefix-icon="Message" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="密码" 
                prefix-icon="Lock" />
            </el-form-item>
            <el-form-item prop="password2">
              <el-input 
                v-model="registerForm.password2" 
                type="password" 
                placeholder="确认密码" 
                prefix-icon="Lock" />
            </el-form-item>
            <el-form-item prop="department">
              <el-select v-model="registerForm.department" placeholder="选择部门" style="width: 100%">
                <el-option label="动画" value="animation" />
                <el-option label="后期" value="post" />
                <el-option label="解算" value="fx" />
                <el-option label="制片" value="producer" />
                <el-option label="模型" value="model" />
              </el-select>
            </el-form-item>
            <el-form-item prop="role">
              <el-select v-model="registerForm.role" placeholder="选择角色" style="width: 100%">
                <el-option label="艺术家" value="artist" />
                <el-option label="带片" value="leader" />
                <el-option label="主管" value="supervisor" />
                <el-option label="制片" value="producer" />
              </el-select>
            </el-form-item>
            <el-form-item prop="registration_notes">
              <el-input 
                v-model="registerForm.registration_notes" 
                type="textarea" 
                placeholder="注册备注（可选）" 
                :rows="2" />
            </el-form-item>
            <el-alert
              v-if="registerMessage"
              :title="registerMessage"
              :type="registerSuccess ? 'success' : 'error'"
              show-icon
              class="register-alert"
            />
            <el-form-item>
              <el-button 
                type="primary" 
                :loading="authStore.loading" 
                class="register-button" 
                @click="handleRegister">
                注册
              </el-button>
            </el-form-item>
            <div class="register-note">
              <p>注册后需要管理员审核才能登录系统</p>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loginFormRef = ref(null)
const registerFormRef = ref(null)
const activeTab = ref('login')
const registerMessage = ref('')
const registerSuccess = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  password2: '',
  role: 'artist',
  department: '',
  registration_notes: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
  ],
  password2: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  department: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    const result = await authStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.error || '登录失败')
    }
  } catch (error) {
    console.error('登录表单验证失败:', error)
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    
    // 确认密码匹配
    if (registerForm.password !== registerForm.password2) {
      ElMessage.error('两次输入的密码不一致')
      return
    }
    
    const result = await authStore.register(registerForm)
    
    if (result.success) {
      registerSuccess.value = true
      registerMessage.value = '注册成功！请等待管理员审核您的账号。'
      
      // 清空表单
      registerForm.username = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.password2 = ''
      registerForm.registration_notes = ''
      
      // 重置表单验证
      registerFormRef.value.resetFields()
      
      // 3秒后切换到登录标签页
      setTimeout(() => {
        activeTab.value = 'login'
      }, 3000)
    } else {
      registerSuccess.value = false
      registerMessage.value = result.error || '注册失败，请稍后重试'
    }
  } catch (error) {
    console.error('注册表单验证失败:', error)
    registerSuccess.value = false
    registerMessage.value = '表单验证失败，请检查输入'
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
  width: 450px;
  padding: 30px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: white;
}

.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #409EFF;
}

.login-form, .register-form {
  margin-top: 20px;
}

.login-button, .register-button {
  width: 100%;
}

.login-tabs {
  margin-top: 15px;
}

.register-note {
  font-size: 12px;
  color: #909399;
  text-align: center;
  margin-top: 10px;
}

.register-alert {
  margin: 10px 0;
}
</style> 