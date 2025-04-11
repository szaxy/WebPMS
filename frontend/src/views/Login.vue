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
            <el-alert
              v-if="loginError"
              :title="loginError"
              type="error"
              show-icon
              :closable="false"
              class="login-alert"
            />
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
            <el-form-item prop="device_code">
              <el-input 
                v-model="registerForm.device_code" 
                placeholder="设备代号" 
                prefix-icon="Monitor" />
              <span class="form-help-text">设备代号是您的工作站标识，格式为5-10位大写字母和数字（如：FTDHDH05）</span>
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
import { ref, reactive, watch } from 'vue'
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
const loginError = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  device_code: '',
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
  device_code: [
    { required: true, message: '请输入设备代号', trigger: 'blur' },
    { pattern: /^[A-Z0-9]{5,10}$/, message: '设备代号格式不正确，应为5-10位大写字母和数字', trigger: 'blur' }
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

// 监听authStore的错误信息
watch(() => authStore.error, (newError) => {
  // 如果有错误信息，赋值给对应表单的错误提示
  if (activeTab.value === 'login') {
    loginError.value = newError
  } else if (activeTab.value === 'register') {
    registerMessage.value = newError
    registerSuccess.value = false
  }
})

// 切换标签页时清除错误
watch(activeTab, () => {
  loginError.value = ''
  registerMessage.value = ''
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    loginError.value = ''
    await loginFormRef.value.validate()
    const result = await authStore.login(loginForm)
    
    if (result.success) {
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      loginError.value = result.error || '登录失败，请检查用户名和密码'
    }
  } catch (error) {
    console.error('登录表单验证失败:', error)
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    registerMessage.value = ''
    registerSuccess.value = false
    await registerFormRef.value.validate()
    
    // 确认密码匹配
    if (registerForm.password !== registerForm.password2) {
      registerMessage.value = '两次输入的密码不一致'
      registerSuccess.value = false
      return
    }
    
    const result = await authStore.register(registerForm)
    
    if (result.success) {
      registerSuccess.value = true
      registerMessage.value = '注册成功！请等待管理员审核您的账号。'
      
      // 清空表单
      registerForm.username = ''
      registerForm.device_code = ''
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

.register-alert, .login-alert {
  margin: 10px 0;
}

.form-help-text {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-top: 5px;
}
</style> 