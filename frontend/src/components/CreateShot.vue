<template>
  <div class="create-shot">
    <el-form
      :model="shotForm"
      :rules="rules"
      ref="formRef"
      label-width="120px"
      class="shot-form"
    >
      <el-form-item label="项目" prop="project">
        <el-select
          v-model="shotForm.project"
          placeholder="请选择项目"
          :loading="loadingProjects"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="`${project.name} (${project.code})`"
            :value="project.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="镜头编号" prop="shot_code">
        <el-input v-model="shotForm.shot_code" placeholder="请输入镜头编号" />
      </el-form-item>
      
      <el-form-item label="状态" prop="status">
        <el-select v-model="shotForm.status" placeholder="请选择状态">
          <el-option label="制作中" value="in_progress" />
          <el-option label="审核中" value="review" />
          <el-option label="已通过" value="approved" />
          <el-option label="需修改" value="need_revision" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="截止日期" prop="deadline">
        <el-date-picker
          v-model="shotForm.deadline"
          type="date"
          placeholder="选择截止日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      
      <el-form-item label="时长(帧)" prop="duration_frame">
        <el-input-number v-model="shotForm.duration_frame" :min="1" />
      </el-form-item>
      
      <el-form-item label="推进阶段" prop="prom_stage">
        <el-input v-model="shotForm.prom_stage" placeholder="请输入推进阶段" />
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="shotForm.description"
          type="textarea"
          rows="3"
          placeholder="请输入镜头描述"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm" :loading="submitting">创建镜头</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '../stores/projectStore'
import { useShotStore } from '../stores/shotStore'

const emit = defineEmits(['created', 'close'])

// 状态管理
const projectStore = useProjectStore()
const shotStore = useShotStore()
const formRef = ref(null)
const loadingProjects = ref(false)
const submitting = ref(false)
const projects = ref([])

// 表单数据
const shotForm = reactive({
  project: '',
  shot_code: '',
  status: 'in_progress',
  deadline: '',
  duration_frame: 0,
  prom_stage: '',
  description: ''
})

// 表单验证规则
const rules = {
  project: [
    { required: true, message: '请选择项目', trigger: 'change' }
  ],
  shot_code: [
    { required: true, message: '请输入镜头编号', trigger: 'blur' },
    { min: 2, message: '镜头编号至少2个字符', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 加载项目列表
const loadProjects = async () => {
  loadingProjects.value = true
  try {
    await projectStore.fetchProjects({ status: 'in_progress' })
    projects.value = projectStore.activeProjects
  } catch (err) {
    console.error('加载项目列表失败:', err)
    ElMessage.error('加载项目列表失败')
  } finally {
    loadingProjects.value = false
  }
}

// 处理项目变更
const handleProjectChange = (projectId) => {
  const project = projects.value.find(p => p.id === projectId)
  if (project) {
    // 可以在这里做一些关联操作，比如自动生成镜头编号前缀等
    shotForm.shot_code = `${project.code}_`
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const shotData = { ...shotForm }
    
    // 创建镜头
    const newShot = await shotStore.createShot(shotData)
    
    ElMessage.success('镜头创建成功')
    
    // 通知父组件
    emit('created', newShot)
    
    // 重置表单
    resetForm()
    
  } catch (err) {
    console.error('创建镜头失败:', err)
    ElMessage.error('创建失败，请检查表单')
  } finally {
    submitting.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  // 重置非表单字段
  shotForm.duration_frame = 0
  shotForm.prom_stage = ''
  shotForm.description = ''
}

// 组件挂载时加载项目列表
onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.create-shot {
  padding: 20px;
}

.shot-form {
  max-width: 500px;
  margin: 0 auto;
}
</style> 