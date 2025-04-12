<template>
  <el-dialog
    v-model="dialogVisible"
    :title="shot ? '编辑镜头' : '新建镜头'"
    width="600px"
    :close-on-click-modal="false"
    @closed="resetForm"
  >
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-width="100px"
      v-loading="loading"
    >
      <el-form-item label="项目" prop="project">
        <el-select v-model="form.project" placeholder="选择项目" style="width: 100%">
          <el-option
            v-for="project in projects"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="镜头编号" prop="shot_code">
        <el-input v-model="form.shot_code" placeholder="请输入镜头编号" />
      </el-form-item>
      
      <el-form-item label="所属部门" prop="department">
        <el-select v-model="form.department" placeholder="选择部门" style="width: 100%">
          <el-option label="动画部门" value="DH" />
          <el-option label="解算部门" value="JS" />
          <el-option label="后期部门" value="HQ" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="推进阶段" prop="prom_stage">
        <el-select v-model="form.prom_stage" placeholder="选择阶段" style="width: 100%">
          <el-option label="Layout" value="LAY" />
          <el-option label="Block" value="BLK" />
          <el-option label="Animation" value="ANI" />
          <el-option label="Pass" value="PASS" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="制作状态" prop="status">
        <el-select v-model="form.status" placeholder="选择状态" style="width: 100%">
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
      </el-form-item>
      
      <el-form-item label="制作者" prop="artist">
        <el-select 
          v-model="form.artist" 
          placeholder="选择制作者" 
          style="width: 100%"
          clearable
        >
          <el-option
            v-for="user in users"
            :key="user.id"
            :label="user.username"
            :value="user.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="帧数" prop="duration_frame">
        <el-input-number v-model="form.duration_frame" :min="0" />
      </el-form-item>
      
      <el-form-item label="截止日期" prop="deadline">
        <el-date-picker
          v-model="form.deadline"
          type="date"
          placeholder="选择截止日期"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="3" 
          placeholder="请输入镜头描述"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="closeDialog">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="submitting">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useShotStore } from '@/stores/shotStore'
import { useProjectStore } from '@/stores/projectStore'
import { useAuthStore } from '@/stores/authStore'

const shotStore = useShotStore()
const projectStore = useProjectStore()
const authStore = useAuthStore()

const props = defineProps({
  shot: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'saved'])

// 对话框可见状态
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

// 表单状态
const formRef = ref(null)
const loading = ref(false)
const submitting = ref(false)
const projects = ref([])
const users = ref([])

// 表单数据
const form = reactive({
  project: null,
  shot_code: '',
  department: 'DH',
  prom_stage: 'LAY',
  status: 'waiting',
  artist: null,
  duration_frame: 0,
  deadline: null,
  description: ''
})

// 表单验证规则
const rules = {
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  shot_code: [{ required: true, message: '请输入镜头编号', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  prom_stage: [{ required: true, message: '请选择推进阶段', trigger: 'change' }],
  status: [{ required: true, message: '请选择制作状态', trigger: 'change' }]
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  
  form.project = null
  form.shot_code = ''
  form.department = 'DH'
  form.prom_stage = 'LAY'
  form.status = 'waiting'
  form.artist = null
  form.duration_frame = 0
  form.deadline = null
  form.description = ''
}

// 监听shot属性变化，填充表单
watch(() => props.shot, (newShot) => {
  if (newShot) {
    form.project = newShot.project
    form.shot_code = newShot.shot_code
    form.department = newShot.department
    form.prom_stage = newShot.prom_stage
    form.status = newShot.status
    form.artist = newShot.artist
    form.duration_frame = newShot.duration_frame
    form.deadline = newShot.deadline
    form.description = newShot.description
  } else {
    resetForm()
  }
}, { immediate: true })

// 初始化函数
onMounted(async () => {
  loading.value = true
  try {
    // 加载项目列表
    await projectStore.fetchProjects()
    projects.value = projectStore.projects
    
    // 加载用户列表（简化版，实际应从用户服务获取）
    users.value = [
      // 这里应该从用户API获取，此处仅为示例
      { id: 1, username: '用户1' },
      { id: 2, username: '用户2' },
      { id: 3, username: '用户3' }
    ]
  } catch (error) {
    console.error('初始化镜头编辑对话框失败', error)
    ElMessage.error('加载数据失败，请刷新页面重试')
  } finally {
    loading.value = false
  }
})

// 关闭对话框
const closeDialog = () => {
  dialogVisible.value = false
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    // 准备提交数据
    const shotData = {
      project: form.project,
      shot_code: form.shot_code,
      department: form.department,
      prom_stage: form.prom_stage,
      status: form.status,
      artist: form.artist,
      duration_frame: form.duration_frame,
      deadline: form.deadline,
      description: form.description
    }
    
    let result
    if (props.shot) {
      // 更新镜头
      result = await shotStore.updateShot(props.shot.id, shotData)
    } else {
      // 创建新镜头
      result = await shotStore.createShot(shotData)
    }
    
    if (result) {
      ElMessage.success(props.shot ? '镜头更新成功' : '镜头创建成功')
      emit('saved', result)
      dialogVisible.value = false
    } else {
      ElMessage.error(shotStore.error || '操作失败')
    }
  } catch (error) {
    console.error('表单验证失败', error)
    ElMessage.error('请检查表单填写是否正确')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.el-select {
  width: 100%;
}
</style> 