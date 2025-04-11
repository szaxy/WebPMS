<template>
  <div class="shot-test">
    <h2>镜头服务测试</h2>
    
    <div v-if="loading" class="loading">
      加载中...
    </div>
    
    <div v-if="error" class="error">
      错误: {{ error }}
    </div>
    
    <div v-if="shots.length" class="shots-list">
      <h3>镜头列表 (共 {{ shots.length }} 个)</h3>
      <table class="shots-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>镜头编号</th>
            <th>部门</th>
            <th>状态</th>
            <th>阶段</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="shot in shots" :key="shot.id">
            <td>{{ shot.id }}</td>
            <td>{{ shot.shot_code }}</td>
            <td>{{ shot.department_display }}</td>
            <td>{{ shot.status_display }}</td>
            <td>{{ shot.prom_stage_display }}</td>
            <td>
              <button @click="viewShot(shot.id)">查看</button>
              <button @click="updateStatus(shot.id, 'in_progress')">设为制作中</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="currentShot" class="shot-details">
      <h3>镜头详情</h3>
      <pre>{{ JSON.stringify(currentShot, null, 2) }}</pre>
      
      <div class="shot-notes">
        <h4>镜头备注 ({{ shotNotes.length }})</h4>
        <div v-for="note in shotNotes" :key="note.id" class="note" :class="{ 'important': note.is_important }">
          <div class="note-header">
            <span class="user">{{ note.user_name }}</span>
            <span class="date">{{ new Date(note.created_at).toLocaleString() }}</span>
          </div>
          <div class="note-content">{{ note.content }}</div>
        </div>
        
        <div class="add-note">
          <h4>添加备注</h4>
          <textarea v-model="newNote.content" placeholder="输入备注内容..."></textarea>
          <label>
            <input type="checkbox" v-model="newNote.isImportant"> 标记为重要
          </label>
          <button @click="addNote">添加备注</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useShotStore } from '../stores/shotStore'
import shotService from '../services/shotService'

export default {
  name: 'ShotTest',
  
  setup() {
    const shotStore = useShotStore()
    
    const shots = ref([])
    const currentShot = ref(null)
    const shotNotes = ref([])
    const loading = ref(false)
    const error = ref(null)
    
    const newNote = ref({
      content: '',
      isImportant: false
    })
    
    onMounted(async () => {
      loading.value = true
      try {
        const response = await shotService.getShots({ limit: 10 })
        shots.value = response.data
      } catch (err) {
        console.error('获取镜头列表失败:', err)
        error.value = '获取镜头列表失败，请检查API连接。'
      } finally {
        loading.value = false
      }
    })
    
    const viewShot = async (id) => {
      loading.value = true
      try {
        const response = await shotService.getShot(id)
        currentShot.value = response.data
        
        // 获取镜头备注
        const notesResponse = await shotService.getShotNotes(id)
        shotNotes.value = notesResponse.data
      } catch (err) {
        console.error(`获取镜头(ID:${id})详情失败:`, err)
        error.value = '获取镜头详情失败。'
      } finally {
        loading.value = false
      }
    }
    
    const updateStatus = async (id, status) => {
      loading.value = true
      try {
        const response = await shotService.updateShotStatus(id, status)
        
        // 更新本地数据
        const index = shots.value.findIndex(s => s.id === id)
        if (index !== -1) {
          shots.value[index] = response.data
        }
        
        if (currentShot.value && currentShot.value.id === id) {
          currentShot.value = response.data
        }
        
        // 检查重要备注
        if (response.data.important_notes && response.data.important_notes.length > 0) {
          alert(`发现${response.data.important_notes.length}条重要备注，请注意查看!`)
        }
      } catch (err) {
        console.error(`更新镜头(ID:${id})状态失败:`, err)
        error.value = '更新镜头状态失败。'
      } finally {
        loading.value = false
      }
    }
    
    const addNote = async () => {
      if (!currentShot.value) {
        error.value = '请先选择一个镜头'
        return
      }
      
      if (!newNote.value.content.trim()) {
        error.value = '备注内容不能为空'
        return
      }
      
      loading.value = true
      try {
        const response = await shotService.addShotNote(currentShot.value.id, {
          content: newNote.value.content,
          isImportant: newNote.value.isImportant
        })
        
        // 添加到备注列表
        shotNotes.value.unshift(response.data)
        
        // 清空表单
        newNote.value.content = ''
        newNote.value.isImportant = false
        
        error.value = null
      } catch (err) {
        console.error('添加备注失败:', err)
        error.value = '添加备注失败。'
      } finally {
        loading.value = false
      }
    }
    
    return {
      shots,
      currentShot,
      shotNotes,
      loading,
      error,
      newNote,
      viewShot,
      updateStatus,
      addNote
    }
  }
}
</script>

<style scoped>
.shot-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: #e74c3c;
  font-weight: bold;
}

.shots-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.shots-table th, .shots-table td {
  padding: 8px 12px;
  border: 1px solid #ddd;
  text-align: left;
}

.shots-table th {
  background-color: #f2f2f2;
}

.shots-table button {
  margin-right: 5px;
  padding: 3px 8px;
}

.shot-details {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.note {
  margin: 10px 0;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.note.important {
  border-left: 4px solid #e74c3c;
}

.note-header {
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
}

.user {
  font-weight: bold;
}

.date {
  color: #777;
  font-size: 0.9em;
}

.add-note {
  margin-top: 20px;
}

.add-note textarea {
  width: 100%;
  min-height: 100px;
  margin-bottom: 10px;
  padding: 8px;
}

.add-note label {
  display: block;
  margin-bottom: 10px;
}

.add-note button {
  padding: 8px 16px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-note button:hover {
  background-color: #2980b9;
}
</style> 