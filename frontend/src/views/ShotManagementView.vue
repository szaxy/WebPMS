<template>
  <div class="shot-management-view">
    <div class="main-header">
      <div class="header-left">
        <el-button type="primary" size="small" icon="Back" @click="goToHome">返回主页</el-button>
        <h1>镜头管理</h1>
      </div>
    </div>
    
    <div class="content-wrapper">
      <!-- 左侧列表区域 -->
      <div class="shot-list-container">
        <ShotList @shot-selected="handleShotSelected" />
      </div>
      
      <!-- 右侧详情区域 -->
      <div class="shot-details-container" v-if="selectedShotId">
        <ShotDetails :shot-id="selectedShotId" />
      </div>
      <div class="empty-details" v-else>
        <el-empty description="选择一个镜头查看详情">
          <template #image>
            <el-icon :size="64"><VideoPlay /></el-icon>
          </template>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ShotList from '@/components/ShotList.vue';
import ShotDetails from '@/components/ShotDetails.vue';
import { VideoPlay, Back } from '@element-plus/icons-vue';

const router = useRouter();

// 选中的镜头ID
const selectedShotId = ref(null);

// 处理镜头选中事件
function handleShotSelected(shotId) {
  selectedShotId.value = shotId;
}

// 返回主页
function goToHome() {
  router.push('/');
}
</script>

<style scoped>
.shot-management-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.shot-list-container {
  width: 65%;
  min-width: 600px;
  border-right: 1px solid var(--el-border-color-light);
  overflow-y: auto;
  padding: 16px;
}

.shot-details-container {
  flex: 1;
  overflow-y: auto;
}

.empty-details {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  color: var(--el-text-color-secondary);
}
</style> 