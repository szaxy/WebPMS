<template>
  <div class="shot-management">
    <!-- 页面内容 -->
    <div class="shot-management-content">
      <!-- 左侧区域 -->
      <div class="left-panel">
        <!-- 筛选区 -->
        <div class="filters-container">
          <div class="page-header">
            <h1 class="page-title">镜头管理</h1>
            <el-button 
              type="primary" 
              size="small" 
              @click="goToHome"
              class="home-button"
            >
              <el-icon><Back /></el-icon> 返回主页
            </el-button>
          </div>
          
          <div class="filters">
            <!-- 项目选择 -->
            <el-select 
              v-model="selectedProject" 
              placeholder="选择项目" 
              clearable 
              @change="handleProjectChange"
              class="filter-item"
              size="small"
            >
              <el-option
                v-for="project in projects.filter(p => p && p.id)"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>

            <!-- 部门筛选 (仅对制片和管理员可见) -->
            <el-select
              v-if="canFilterByDepartment"
              v-model="filters.department"
              placeholder="部门"
              clearable
              @change="applyFilters"
              class="filter-item"
              size="small"
            >
              <el-option label="动画部门" value="animation" />
              <el-option label="解算部门" value="fx" />
              <el-option label="后期部门" value="post" />
              <el-option label="模型部门" value="model" />
            </el-select>

            <!-- 推进阶段筛选 -->
            <el-select
              v-model="filters.prom_stage"
              placeholder="推进阶段"
              clearable
              @change="applyFilters"
              class="filter-item"
              size="small"
            >
              <el-option label="Layout" value="LAY" />
              <el-option label="Block" value="BLK" />
              <el-option label="Animation" value="ANI" />
              <el-option label="Pass" value="PASS" />
            </el-select>

            <!-- 状态筛选 -->
            <el-select
              v-model="filters.status"
              placeholder="制作状态"
              clearable
              @change="applyFilters"
              class="filter-item"
              size="small"
            >
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

            <!-- 搜索框 -->
            <el-input
              v-model="searchQuery"
              placeholder="搜索镜头号..."
              clearable
              @input="applyFilters"
              class="filter-item search-input"
              size="small"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>

            <!-- 高级筛选按钮 -->
            <el-dropdown @command="handleAdvancedFilter" trigger="click">
              <el-button type="primary" plain size="small">
                高级筛选
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="hasComments">有反馈的镜头</el-dropdown-item>
                  <el-dropdown-item command="hasNotes">有备注的镜头</el-dropdown-item>
                  <el-dropdown-item command="hasImportantNotes">有重要备注的镜头</el-dropdown-item>
                  <el-dropdown-item command="overdueDeadline">已逾期镜头</el-dropdown-item>
                  <el-dropdown-item command="upcomingDeadline">临近截止日期镜头</el-dropdown-item>
                  <el-dropdown-item command="clearAll">清除所有筛选</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            
            <!-- 展示项按钮 -->
            <el-button size="small" @click="columnDialogVisible = true">
              展示项
            </el-button>
          </div>
        </div>

        <!-- 镜头列表区域 -->
        <div class="shot-list-area">
          <el-card class="shot-list-card">
            <template #header>
              <div class="list-header">
                <div class="list-title">
                  镜头列表
                  <el-tag v-if="filteredShots.length">{{ filteredShots.length }}个镜头</el-tag>
                </div>
                <div class="list-actions">
                  <el-button-group>
                    <el-button @click="openAddShotDialog" title="添加" size="small">
                      <el-icon><Plus /></el-icon>
                    </el-button>
                    <el-button @click="openProjectManagement" title="项目" size="small">
                      <el-icon><Briefcase /></el-icon>
                    </el-button>
                    <el-button @click="refreshShots" title="刷新" size="small">
                      <el-icon><Refresh /></el-icon>
                    </el-button>
                    <el-button @click="exportShots" title="导出" size="small">
                      <el-icon><Download /></el-icon>
                    </el-button>
                  </el-button-group>
                </div>
              </div>
              
              <!-- 批量操作工具栏 -->
              <div class="batch-actions" v-if="shotStore.selectedShotIds.length > 0">
                <div class="selected-info">
                  已选择 <strong>{{ shotStore.selectedShotIds.length }}</strong> 个镜头
                </div>
                <div class="action-buttons">
                  <el-button type="danger" @click="confirmBatchDelete" size="small">
                    <el-icon><Delete /></el-icon> 删除
                  </el-button>
                  <el-button type="info" @click="clearSelection" size="small">
                    <el-icon><Close /></el-icon> 取消选择
                  </el-button>
                </div>
              </div>
            </template>

            <!-- 镜头表格 -->
            <el-table
              ref="shotTable"
              v-loading="loading"
              :data="filteredShots"
              @row-click="handleRowClick"
              :highlight-current-row="true"
              style="width: 100%"
              :max-height="tableHeight"
              stripe
              border
              @selection-change="handleSelectionChange"
              table-layout="fixed"
            >
              <!-- 诊断信息 -->
              <template v-if="filteredShots.length === 0 && !loading" #empty>
                <div style="padding: 20px; text-align: left;">
                  <h3>未找到镜头数据，请检查以下信息：</h3>
                  <p><strong>当前项目:</strong> {{ selectedProject ? projects.find(p => p.id === selectedProject)?.name : '未选择项目' }}</p>
                  <p><strong>当前用户角色:</strong> {{ authStore.user?.role || '未知' }}</p>
                  <p><strong>当前用户部门:</strong> {{ userDepartment || '未知' }}</p>
                  <p><strong>应用筛选:</strong> {{ JSON.stringify(filters) }}</p>
                  <p><strong>搜索关键字:</strong> {{ searchQuery || '无' }}</p>
                  <p><strong>项目总数:</strong> {{ projects.length }}</p>
                  <div v-if="shotStore.error" class="error-message">
                    <strong>错误信息:</strong> {{ shotStore.error }}
                  </div>
                  <el-button type="primary" @click="refreshShots">刷新数据</el-button>
                </div>
              </template>
              
              <!-- 状态标记列 -->
              <el-table-column type="selection" width="40" fixed />
              
              <!-- 常规列 -->
              <el-table-column v-if="isColumnVisible('shot_code')" prop="shot_code" label="镜头号" fixed width="180" sortable>
                <template #default="{ row }">
                  <div class="shot-code-container">
                    <span>{{ row.shot_code }}</span>
                    <div class="status-indicators" v-if="row.has_comments || row.has_notes || row.has_important_notes">
                      <el-tooltip v-if="row.has_comments" content="有反馈">
                        <div class="indicator comment-indicator"></div>
                      </el-tooltip>
                      <el-tooltip v-if="row.has_notes" content="有备注">
                        <div class="indicator note-indicator"></div>
                      </el-tooltip>
                      <el-tooltip v-if="row.has_important_notes" content="有重要备注">
                        <div class="indicator important-note-indicator"></div>
                      </el-tooltip>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column v-if="isColumnVisible('duration_frame')" prop="duration_frame" label="帧数" width="80" sortable />
              
              <el-table-column v-if="isColumnVisible('prom_stage')" label="推进阶段" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStageTagType(row.prom_stage)">
                    {{ row.prom_stage_display }}
                  </el-tag>
                </template>
              </el-table-column>
              
              <el-table-column v-if="isColumnVisible('status')" label="制作状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)">
                    {{ row.status_display }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('artist')" label="制作者" width="100">
                <template #default="{ row }">
                  {{ row.artist_name || '-' }}
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('deadline')" label="截止日期" width="100" sortable>
                <template #default="{ row }">
                  <span :class="getDeadlineClass(row)">
                    {{ formatDate(row.deadline) }}
                  </span>
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('last_submit_date')" label="最近提交" width="100" sortable>
                <template #default="{ row }">
                  <span :class="getSubmitDateClass(row)">
                    {{ formatDate(row.last_submit_date) }}
                  </span>
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('department')" label="部门" width="80">
                <template #default="{ row }">
                  {{ row.department_display }}
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('description')" label="描述" width="150">
                <template #default="{ row }">
                  <el-tooltip 
                    v-if="row.description" 
                    :content="row.description" 
                    placement="top-start" 
                    :show-after="500"
                    :enterable="false"
                  >
                    <span>{{ truncateText(row.description, 15) }}</span>
                  </el-tooltip>
                  <span v-else>-</span>
                </template>
              </el-table-column>

              <el-table-column v-if="isColumnVisible('updated_at')" label="更新时间" width="160" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[20, 50, 100, 200]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="totalShotsCount"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
              />
            </div>
          </el-card>
        </div>
      </div>

      <!-- 右侧详情区域 -->
      <div class="right-panel">
        <div v-if="selectedShot" class="shot-details-container">
          <ShotDetails 
            :shot="selectedShot" 
            @update="handleShotUpdate" 
            @close="selectedShot = null" 
          />
        </div>
        <div v-else class="empty-details">
          <el-empty description="请选择一个镜头以展示详情" />
        </div>
      </div>
    </div>
  </div>
  
  <!-- 列设置对话框 -->
  <el-dialog
    v-model="columnDialogVisible"
    title="列展示设置"
    width="400px"
  >
    <el-checkbox-group v-model="visibleColumns" @change="saveColumnSettings">
      <div class="column-options">
        <el-checkbox v-for="column in allColumns" :key="column.prop" :value="column.prop">
          {{ column.label }}
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <template #footer>
      <el-button @click="columnDialogVisible = false">关闭</el-button>
    </template>
  </el-dialog>
  
  <!-- 添加镜头对话框 -->
  <el-dialog
    v-model="addShotDialogVisible"
    title="添加镜头"
    width="650px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeAddTab">
      <!-- 单个添加选项卡 -->
      <el-tab-pane label="单个添加" name="single">
        <el-form :model="singleShotForm" label-width="90px" label-position="right" size="small" :inline="true">
          <div style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 10px;">
            <el-form-item label="所属项目" required>
              <el-select 
                v-model="singleShotForm.project" 
                placeholder="选择项目" 
                style="width: 100%"
                filterable
                clearable
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="镜头号" required>
              <el-input v-model="singleShotForm.shot_code" placeholder="输入镜头号" />
            </el-form-item>
            
            <el-form-item label="帧数" required>
              <el-input-number v-model="singleShotForm.duration_frame" :min="1" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="帧率" required>
              <el-input-number v-model="singleShotForm.framepersecond" :min="1" :precision="0" :step="1" :default="24" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="制作者" required>
              <el-select 
                v-model="singleShotForm.artist" 
                placeholder="选择制作者"
                filterable 
                clearable
                style="width: 100%"
              >
                <el-option label="待实现用户选择" value="" disabled />
              </el-select>
            </el-form-item>
            
            <el-form-item label="推进阶段">
              <el-select 
                v-model="singleShotForm.prom_stage" 
                placeholder="选择推进阶段"
                style="width: 100%"
              >
                <el-option label="Layout" value="LAY" />
                <el-option label="Block" value="BLK" />
                <el-option label="Animation" value="ANI" />
                <el-option label="Pass" value="PASS" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="截止日期" prop="deadline">
              <el-date-picker
                v-model="singleShotForm.deadline"
                type="date"
                placeholder="选择截止日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                :clearable="true"
                :shortcuts="false"
                :editable="false"
                :popper-class="'shot-deadline-picker'"
                @change="handleSingleDeadlineChange"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="最近提交日期" prop="last_submit_date">
              <el-date-picker
                v-model="singleShotForm.last_submit_date"
                type="date"
                placeholder="选择最近提交日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                :clearable="true"
                :shortcuts="false"
                :editable="false"
                :popper-class="'shot-submit-date-picker'"
                @change="handleSingleSubmitDateChange"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          
          <el-form-item label="描述" style="width: 100%">
            <el-input
              v-model="singleShotForm.description"
              type="textarea"
              :rows="2"
              placeholder="输入镜头描述"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 批量添加选项卡 -->
      <el-tab-pane label="批量添加" name="batch">
        <el-form :model="batchShotForm" label-width="90px" label-position="right" size="small">
          <el-form-item label="所属项目" required>
            <el-select 
              v-model="batchShotForm.project" 
              placeholder="选择项目" 
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="命名规则">
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-input v-model="batchShotForm.prefix" placeholder="前缀" style="width: 80px" />
              <span>+</span>
              <div style="display: flex; align-items: center; gap: 5px;">
                <span>数字</span>
                <el-tooltip content="数字位数">
                  <el-input-number v-model="batchShotForm.digit_count" :min="1" :max="6" style="width: 90px" />
                </el-tooltip>
              </div>
              <span>+</span>
              <el-input v-model="batchShotForm.suffix" placeholder="后缀" style="width: 80px" />
            </div>
          </el-form-item>
          
          <el-form-item label="数字规则">
            <div style="display: flex; align-items: center; gap: 10px;">
              <div style="display: flex; flex-direction: column; gap: 5px;">
                <span>起始值</span>
                <el-input-number v-model="batchShotForm.start_num" :min="0" />
              </div>
              <div style="display: flex; flex-direction: column; gap: 5px;">
                <span>步长</span>
                <el-input-number v-model="batchShotForm.step" :min="1" />
              </div>
              <div style="display: flex; flex-direction: column; gap: 5px;">
                <span>数量</span>
                <el-input-number v-model="batchShotForm.count" :min="1" :max="100" />
              </div>
            </div>
          </el-form-item>

          <div style="display: grid; grid-template-columns: 1fr 1fr; column-gap: 10px;">
            <el-form-item label="帧数" required>
              <el-input-number v-model="batchShotForm.duration_frame" :min="1" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="帧率" required>
              <el-input-number v-model="batchShotForm.framepersecond" :min="1" :precision="0" :step="1" :default="24" style="width: 100%" />
            </el-form-item>
            
            <el-form-item label="推进阶段">
              <el-select v-model="batchShotForm.prom_stage" style="width: 100%">
                <el-option label="Layout" value="LAY" />
                <el-option label="Block" value="BLK" />
                <el-option label="Animation" value="ANI" />
                <el-option label="Pass" value="PASS" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="截止日期" prop="deadline">
              <el-date-picker
                v-model="batchShotForm.deadline"
                type="date"
                placeholder="选择截止日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                :clearable="true"
                :shortcuts="false"
                :editable="false"
                :popper-class="'shot-deadline-picker'"
                @change="handleBatchDeadlineChange"
                style="width: 100%"
              />
            </el-form-item>
            
            <el-form-item label="最近提交日期" prop="last_submit_date">
              <el-date-picker
                v-model="batchShotForm.last_submit_date"
                type="date"
                placeholder="选择最近提交日期"
                value-format="YYYY-MM-DD"
                format="YYYY-MM-DD"
                :clearable="true"
                :shortcuts="false"
                :editable="false"
                :popper-class="'shot-submit-date-picker'"
                @change="handleBatchSubmitDateChange"
                style="width: 100%"
              />
            </el-form-item>
          </div>
          
          <el-form-item label="预览">
            <div class="preview-container" v-if="batchShotNamePreview.length > 0">
              <div class="preview-tags">
                <el-tag 
                  v-for="(name, index) in batchShotNamePreview.slice(0, 10)" 
                  :key="index"
                  class="preview-tag"
                >
                  {{ name }}
                </el-tag>
              </div>
              <div v-if="batchShotNamePreview.length > 10" class="preview-more">
                ...共 {{ batchShotNamePreview.length }} 个镜头
              </div>
            </div>
            <div v-else class="no-preview">
              请设置命名规则和数量以查看预览
            </div>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      
      <!-- 导入镜头选项卡 -->
      <el-tab-pane label="导入镜头" name="import">
        <div class="import-placeholder" style="padding: 20px 0; text-align: center;">
          <el-icon style="font-size: 48px; color: #909399; margin-bottom: 10px"><Connection /></el-icon>
          <div style="font-size: 16px; margin-bottom: 10px;">导入镜头功能正在开发中</div>
          <div style="color: #909399; font-size: 14px;">敬请期待...</div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <template #footer>
      <el-button @click="addShotDialogVisible = false">取消</el-button>
      <el-button 
        type="primary" 
        @click="submitAddShot" 
        :disabled="activeAddTab === 'import'"
      >
        确认添加
      </el-button>
    </template>
  </el-dialog>
  
  <!-- 镜头编辑对话框 -->
  <ShotEditDialog
    v-model:visible="editDialogVisible"
    :shot="currentEditShot"
    @saved="handleShotSaved"
  />
  
  <!-- 项目管理对话框 -->
  <ProjectManagement
    v-model:visible="projectManagementVisible"
    @refresh="handleProjectRefresh"
  />
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { Search, Refresh, Download, ArrowDown, Delete, Close, Plus, Connection, Back, Briefcase } from '@element-plus/icons-vue'
import { useShotStore } from '@/stores/shotStore'
import { useProjectStore } from '@/stores/projectStore'
import { useAuthStore } from '@/stores/authStore'
import { usePermissions } from '@/composables/usePermissions'
import ShotDetails from '@/components/ShotDetails.vue'
import ShotEditDialog from '@/components/ShotEditDialog.vue'
import ProjectManagement from '@/components/ProjectManagement.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatDate, formatDateTime, getDeadlineClass, getSubmitDateClass } from '@/utils/dateUtils'
import { getStatusTagType, getStageTagType } from '@/utils/statusUtils'
import { truncateText } from '@/utils/stringUtils'
import { useRouter } from 'vue-router'

// 店铺
const shotStore = useShotStore()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const router = useRouter()
// 使用权限组合式API
const permissions = usePermissions()

// 数据
const loading = ref(false)
const selectedProject = ref(null)
const searchQuery = ref('')
const selectedShot = ref(null)
const shotTable = ref(null)
const tableHeight = ref(600)
const currentPage = ref(1)
const pageSize = ref(50)
const totalShotsCount = ref(0)
const editDialogVisible = ref(false)
const currentEditShot = ref(null)
const columnDialogVisible = ref(false)
const addShotDialogVisible = ref(false)
const activeAddTab = ref('single')

// 单个添加镜头表单
const singleShotForm = reactive({
  project: '',
  shot_code: '',
  duration_frame: 24,
  framepersecond: 24,
  artist: '',
  prom_stage: 'LAY',
  deadline: '',
  last_submit_date: '',
  description: ''
})

// 批量添加镜头表单
const batchShotForm = reactive({
  project: '',
  prefix: 'SC_',
  start_num: 10,
  suffix: '',
  step: 10,
  count: 5,
  digit_count: 3,
  prom_stage: 'LAY',
  deadline: '',
  framepersecond: 24,
  duration_frame: 24,
  last_submit_date: '',
})

// 批量添加预览
const batchShotNamePreview = computed(() => {
  if (!batchShotForm.prefix && !batchShotForm.suffix && !batchShotForm.start_num && !batchShotForm.count) {
    return []
  }
  
  const result = []
  const digitCount = batchShotForm.digit_count || 3
  
  for (let i = 0; i < batchShotForm.count; i++) {
    const num = batchShotForm.start_num + (i * batchShotForm.step)
    const numStr = num.toString().padStart(digitCount, '0')
    const name = `${batchShotForm.prefix || ''}${numStr}${batchShotForm.suffix || ''}`
    result.push(name)
  }
  
  return result
})

// 用户角色和权限 - 使用权限服务
const canFilterByDepartment = permissions.canFilterByDepartment
const canViewAllShots = permissions.canViewAllShots
const canDeleteShots = permissions.canDeleteShot
const canCreateShot = computed(() => true) // 默认所有用户都可以创建镜头

// 获取用户部门
const userDepartment = computed(() => {
  // 当用户角色是admin时，直接返回"管理员"
  if (permissions.currentUserRole.value === 'admin') {
    return '管理员'
  }
  return permissions.currentUserDepartment.value || '未知'
})

// 筛选
const filters = reactive({
  department: null, // 初始化为null，会在组件挂载时根据用户角色设置
  prom_stage: null,
  status: null,
  has_comments: null,
  has_notes: null,
  has_important_notes: null,
  artist: null,
  deadline_from: null,
  deadline_to: null
})

// 列设置
const allColumns = [
  { prop: 'shot_code', label: '镜头号' },
  { prop: 'duration_frame', label: '帧数' },
  { prop: 'framepersecond', label: '帧率' },
  { prop: 'prom_stage', label: '推进阶段' },
  { prop: 'status', label: '制作状态' },
  { prop: 'artist', label: '制作者' },
  { prop: 'deadline', label: '截止日期' },
  { prop: 'last_submit_date', label: '最近提交' },
  { prop: 'department', label: '部门' },
  { prop: 'description', label: '描述' },
  { prop: 'updated_at', label: '更新时间' }
]

// 初始可见列
const visibleColumns = ref([
  'shot_code', 'duration_frame', 'prom_stage', 'status', 
  'artist', 'deadline', 'last_submit_date'
])

// 加载项目列表
const projects = ref([])
const loadProjects = async () => {
  try {
    console.log('开始加载项目列表')
    const projectList = await projectStore.fetchProjects()
    console.log('原始项目数据:', projectList)
    
    // 确保项目列表是有效的数组，并且每个项目都有id
    if (Array.isArray(projectList)) {
      projects.value = projectList.filter(p => p && typeof p === 'object' && p.id)
      console.log('过滤后的项目列表:', projects.value)
    } else if (projectList && Array.isArray(projectList.results)) {
      // 处理分页响应
      projects.value = projectList.results.filter(p => p && typeof p === 'object' && p.id)
      console.log('从分页结果中过滤的项目列表:', projects.value)
    } else {
      console.error('项目数据格式不正确:', projectList)
      projects.value = []
    }
    
    // 如果有项目，默认选择第一个
    if (projects.value.length > 0 && !selectedProject.value) {
      console.log('自动选择第一个项目:', projects.value[0])
      selectedProject.value = projects.value[0].id
      await loadShots()
    } else if (projects.value.length === 0) {
      // 如果没有项目，显示提示
      console.warn('未找到任何项目')
      ElMessage({
        message: '暂无可用项目',
        type: 'info'
      })
    } else {
      console.log('使用当前选择的项目:', selectedProject.value)
    }
  } catch (error) {
    console.error('加载项目失败', error)
    if (error.response) {
      console.error('错误状态:', error.response.status)
      console.error('错误数据:', error.response.data)
    }
    ElMessage({
      message: '加载项目失败，请刷新页面重试',
      type: 'error'
    })
    projects.value = [] // 确保设置为空数组而不是undefined
  }
}

// 加载镜头列表
const loadShots = async () => {
  if (!selectedProject.value) {
    // 没有选择项目时，清空镜头列表
    shotStore.shots = []
    totalShotsCount.value = 0
    return
  }
  
  loading.value = true
  try {
    console.log('开始加载镜头，项目ID:', selectedProject.value)
    
    // 构建基本参数
    const params = {
      project: selectedProject.value,
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
      search: searchQuery.value || undefined,
    }
    
    // 添加有效的筛选条件（过滤掉null/undefined值）
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        params[key] = value;
      }
    });
    
    // 使用权限服务获取部门访问限制
    const accessibleDepartment = permissions.canAccessShotsByDepartment.value
    if (accessibleDepartment && !params.department) {
      console.log('用户部门限制，部门值:', accessibleDepartment)
      params.department = accessibleDepartment
    }
    
    console.log('请求参数:', params)
    
    const response = await shotStore.fetchShots(params)
    console.log('API响应:', response)
    
    totalShotsCount.value = response?.count || 0
    
    if (shotStore.shots.length === 0) {
      console.log('没有找到镜头，用户角色:', permissions.currentUserRole.value, '用户部门:', permissions.currentUserDepartment.value)
      ElMessage({ 
        message: '没有找到符合条件的镜头', 
        type: 'info' 
      })
    } else {
      console.log(`成功加载 ${shotStore.shots.length} 个镜头，用户部门: ${permissions.currentUserDepartment.value}`)
    }
  } catch (error) {
    console.error('加载镜头失败', error)
    ElMessage({ 
      message: '加载镜头失败，请检查网络连接或刷新页面', 
      type: 'error' 
    })
    shotStore.shots = []
    totalShotsCount.value = 0
  } finally {
    loading.value = false
  }
}

// 过滤后的镜头列表
const filteredShots = computed(() => {
  return shotStore.shots
})

// 处理项目变更
const handleProjectChange = async () => {
  currentPage.value = 1
  await loadShots()
}

// 应用筛选
const applyFilters = async () => {
  currentPage.value = 1
  await loadShots()
}

// 刷新镜头列表
const refreshShots = async () => {
  await loadShots()
}

// 导出镜头列表
const exportShots = () => {
  // TODO: 实现导出功能
  ElMessage({
    message: '导出功能开发中...',
    type: 'info'
  })
}

// 表格行选择变化
const handleSelectionChange = (selection) => {
  shotStore.selectAllShots(false) // 先清空
  selection.forEach(shot => {
    shotStore.selectShot(shot.id)
  })
}

// 处理行点击
const handleRowClick = (row) => {
  selectedShot.value = { ...row }
}

// 编辑镜头
const editShot = (shot) => {
  try {
    // 使用权限服务检查编辑权限
    if (!permissions.canEditShot(shot).value) {
      ElMessage.warning('您没有权限编辑此镜头')
      return
    }
    
    currentEditShot.value = shot
    editDialogVisible.value = true
  } catch (error) {
    console.error('权限检查失败:', error)
    ElMessage.error('权限检查时出错')
  }
}

// 处理镜头更新
const handleShotUpdate = (updatedShot) => {
  try {
    // 刷新当前选中的镜头数据
    if (selectedShot.value && selectedShot.value.id === updatedShot.id) {
      selectedShot.value = updatedShot
    }
    
    // 刷新镜头列表中的数据
    const index = shotStore.shots.findIndex(s => s.id === updatedShot.id)
    if (index !== -1) {
      shotStore.shots[index] = updatedShot
    }
  } catch (error) {
    console.error('更新镜头数据失败:', error)
    ElMessage.error('更新镜头数据失败')
  }
}

// 处理高级筛选
const handleAdvancedFilter = (command) => {
  switch (command) {
    case 'hasComments':
      filters.has_comments = true
      filters.has_notes = null
      filters.has_important_notes = null
      break
    case 'hasNotes':
      filters.has_comments = null
      filters.has_notes = true
      filters.has_important_notes = null
      break
    case 'hasImportantNotes':
      filters.has_comments = null
      filters.has_notes = null
      filters.has_important_notes = true
      break
    case 'overdueDeadline':
      const today = new Date()
      filters.deadline_to = today.toISOString().split('T')[0]
      break
    case 'upcomingDeadline':
      const now = new Date()
      const nextWeek = new Date(now)
      nextWeek.setDate(now.getDate() + 7)
      
      filters.deadline_from = now.toISOString().split('T')[0]
      filters.deadline_to = nextWeek.toISOString().split('T')[0]
      break
    case 'clearAll':
      Object.keys(filters).forEach(key => {
        filters[key] = null
      })
      searchQuery.value = ''
      break
  }
  
  applyFilters()
}

// 处理页码变更
const handleCurrentChange = async (page) => {
  currentPage.value = page
  await loadShots()
}

// 处理每页条数变更
const handleSizeChange = async (size) => {
  pageSize.value = size
  currentPage.value = 1
  await loadShots()
}

// 列可见性
const isColumnVisible = (prop) => {
  return visibleColumns.value.includes(prop)
}

// 保存列设置
const saveColumnSettings = () => {
  localStorage.setItem('shotColumns', JSON.stringify(visibleColumns.value))
}

// 加载列设置
const loadColumnSettings = () => {
  const savedColumns = localStorage.getItem('shotColumns')
  if (savedColumns) {
    visibleColumns.value = JSON.parse(savedColumns)
  }
}

// 表格调整高度
const resizeTable = () => {
  nextTick(() => {
    // 动态计算表格高度，考虑页面其他元素的高度
    const windowHeight = window.innerHeight
    // 减去其他UI元素的高度 (头部、分页、内边距等)
    const otherElementsHeight = 240 
    tableHeight.value = windowHeight - otherElementsHeight
  })
}

// 添加窗口大小变化的监听器
window.addEventListener('resize', resizeTable)

// 生命周期钩子
onMounted(async () => {
  try {
    // 如果用户未登录，获取用户信息
    if (!authStore.user) {
      await authStore.fetchCurrentUser()
    }
    
    // 加载项目和镜头数据
    await loadProjects()
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage({
      message: '初始化失败，请刷新页面重试',
      type: 'error'
    })
  }
})

onUnmounted(() => {
  // 清理监听器
  window.removeEventListener('resize', resizeTable)
})

// 处理镜头保存
const handleShotSaved = async (updatedShot) => {
  ElMessage.success('镜头保存成功')
  await refreshShots()
  currentEditShot.value = null
}

// 确认删除单个镜头
const confirmDeleteShot = (shot) => {
  try {
    // 使用权限服务检查删除权限
    if (!permissions.canDeleteShot.value) {
      ElMessage.warning('您没有权限删除镜头')
      return
    }
    
    ElMessageBox.confirm(
      `确定要删除镜头 "${shot.shot_code}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
      .then(async () => {
        try {
          await shotStore.deleteShot(shot.id)
          ElMessage.success('镜头删除成功')
          // 如果当前选中的是被删除的镜头，清空选择
          if (selectedShot.value?.id === shot.id) {
            selectedShot.value = null
          }
          await refreshShots()
        } catch (error) {
          console.error('删除镜头失败', error)
          ElMessage.error('删除镜头失败')
        }
      })
      .catch(() => {
        ElMessage.info('已取消删除')
      })
  } catch (error) {
    console.error('权限检查失败:', error)
    ElMessage.error('权限检查时出错')
  }
}

// 确认批量删除
const confirmBatchDelete = () => {
  try {
    if (shotStore.selectedShotIds.length === 0) {
      ElMessage.warning('请选择要删除的镜头')
      return
    }
    
    // 使用权限服务检查删除权限
    if (!permissions.canDeleteShot.value) {
      ElMessage.warning('您没有权限删除镜头')
      return
    }
    
    ElMessageBox.confirm(
      `确定要删除选中的 ${shotStore.selectedShotIds.length} 个镜头吗？此操作不可恢复。`,
      '批量删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        loading.value = true
        
        // 逐个删除，提高成功率
        let successCount = 0
        let failCount = 0
        const totalCount = shotStore.selectedShotIds.length
        
        // 复制一份ID列表以避免在循环中修改
        const idsToDelete = [...shotStore.selectedShotIds]
        
        console.log(`开始批量删除 ${idsToDelete.length} 个镜头...`)
        for (const id of idsToDelete) {
          try {
            const success = await shotStore.deleteShot(id)
            if (success) {
              successCount++
            } else {
              failCount++
            }
          } catch (err) {
            console.error(`删除镜头 ${id} 时发生错误:`, err)
            failCount++
          }
        }
        
        // 汇总结果
        if (successCount > 0) {
          ElMessage.success(`成功删除 ${successCount} 个镜头`)
        }
        
        if (failCount > 0) {
          ElMessage.warning(`有 ${failCount} 个镜头删除失败`)
        }
        
        // 清空选择
        shotStore.selectAllShots(false)
        
        // 刷新列表
        await refreshShots()
      } catch (error) {
        console.error('批量删除过程中发生错误:', error)
        ElMessage.error('批量删除过程中发生错误，请检查控制台日志')
      } finally {
        loading.value = false
      }
    }).catch(() => {
      // 用户取消删除，不执行任何操作
    })
  } catch (error) {
    console.error('权限检查失败:', error)
    ElMessage.error('权限检查时出错')
  }
}

// 清除选择
const clearSelection = () => {
  shotStore.selectAllShots(false)
  if (shotTable.value) {
    shotTable.value.clearSelection()
  }
}

// 打开添加镜头对话框
const openAddShotDialog = () => {
  // 预先填充项目ID
  singleShotForm.project = selectedProject.value || ''
  batchShotForm.project = selectedProject.value || ''
  
  addShotDialogVisible.value = true
}

// 处理添加镜头
const submitAddShot = async () => {
  try {
    if (activeAddTab.value === 'single') {
      // 验证单个镜头表单
      if (!singleShotForm.project) {
        ElMessage.error('请选择项目')
        return
      }
      if (!singleShotForm.shot_code) {
        ElMessage.error('请输入镜头号')
        return
      }
      if (!singleShotForm.duration_frame || singleShotForm.duration_frame <= 0) {
        ElMessage.error('请输入有效的帧数')
        return
      }
      if (!singleShotForm.framepersecond || singleShotForm.framepersecond <= 0) {
        ElMessage.error('请输入有效的帧率')
        return
      }

      // 确保日期数据的正确性
      const shotFormData = { ...singleShotForm }
      
      // 确保日期格式正确 - 日期字段深度处理
      if (shotFormData.deadline) {
        // 验证日期格式
        if (typeof shotFormData.deadline === 'string') {
          const dateMatch = shotFormData.deadline.match(/^(\d{4})-(\d{2})-(\d{2})$/)
          if (dateMatch) {
            // 保持格式不变，但确保是合法日期
            const year = parseInt(dateMatch[1])
            const month = parseInt(dateMatch[2]) - 1 // JS月份从0开始
            const day = parseInt(dateMatch[3])
            
            const dateObj = new Date(year, month, day)
            if (
              dateObj.getFullYear() === year &&
              dateObj.getMonth() === month &&
              dateObj.getDate() === day
            ) {
              // 日期有效，重新格式化确保一致
              shotFormData.deadline = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            } else {
              console.error('日期无效:', shotFormData.deadline)
              delete shotFormData.deadline
            }
          } else {
            console.error('日期格式错误:', shotFormData.deadline)
            delete shotFormData.deadline
          }
        } else if (shotFormData.deadline instanceof Date) {
          if (!isNaN(shotFormData.deadline.getTime())) {
            shotFormData.deadline = shotFormData.deadline.toISOString().split('T')[0]
          } else {
            console.error('日期对象无效:', shotFormData.deadline)
            delete shotFormData.deadline
          }
        } else {
          console.error('未知日期类型:', typeof shotFormData.deadline)
          delete shotFormData.deadline
        }
      }
      
      // 同样处理最近提交日期
      if (shotFormData.last_submit_date) {
        // 验证日期格式
        if (typeof shotFormData.last_submit_date === 'string') {
          const dateMatch = shotFormData.last_submit_date.match(/^(\d{4})-(\d{2})-(\d{2})$/)
          if (dateMatch) {
            // 保持格式不变，但确保是合法日期
            const year = parseInt(dateMatch[1])
            const month = parseInt(dateMatch[2]) - 1 // JS月份从0开始
            const day = parseInt(dateMatch[3])
            
            const dateObj = new Date(year, month, day)
            if (
              dateObj.getFullYear() === year &&
              dateObj.getMonth() === month &&
              dateObj.getDate() === day
            ) {
              // 日期有效，重新格式化确保一致
              shotFormData.last_submit_date = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
            } else {
              console.error('提交日期无效:', shotFormData.last_submit_date)
              delete shotFormData.last_submit_date
            }
          } else {
            console.error('提交日期格式错误:', shotFormData.last_submit_date)
            delete shotFormData.last_submit_date
          }
        } else if (shotFormData.last_submit_date instanceof Date) {
          if (!isNaN(shotFormData.last_submit_date.getTime())) {
            shotFormData.last_submit_date = shotFormData.last_submit_date.toISOString().split('T')[0]
          } else {
            console.error('提交日期对象无效:', shotFormData.last_submit_date)
            delete shotFormData.last_submit_date
          }
        } else {
          console.error('未知提交日期类型:', typeof shotFormData.last_submit_date)
          delete shotFormData.last_submit_date
        }
      }

      // 调试日期值
      console.log('表单提交前日期值:', {
        原始日期: singleShotForm.deadline,
        原始类型: typeof singleShotForm.deadline,
        处理后日期: shotFormData.deadline,
        处理后类型: typeof shotFormData.deadline,
        原始提交日期: singleShotForm.last_submit_date,
        原始提交类型: typeof singleShotForm.last_submit_date,
        处理后提交日期: shotFormData.last_submit_date,
        处理后提交类型: typeof shotFormData.last_submit_date
      })

      // 开始创建镜头
      loading.value = true
      const newShot = await shotStore.createShot(shotFormData)
      if (newShot) {
        ElMessage.success(`镜头 ${newShot.shot_code} 创建成功`)
        await refreshShots()
      } else {
        ElMessage.error('创建镜头失败')
      }
      
      // 添加return语句，防止代码继续执行到批量添加逻辑
      return
    }
    
    // 批量添加逻辑
    if (!batchShotForm.project) {
      ElMessage.error('请选择项目')
      return
    }
    if (!batchShotForm.prefix) {
      ElMessage.error('请输入前缀')
      return
    }
    if (!batchShotForm.start_num || batchShotForm.start_num < 0) {
      ElMessage.error('请输入有效的起始编号')
      return
    }
    if (!batchShotForm.count || batchShotForm.count <= 0 || batchShotForm.count > 100) {
      ElMessage.error('请输入有效的数量（1-100）')
      return
    }
    if (!batchShotForm.digit_count || batchShotForm.digit_count <= 0) {
      ElMessage.error('请输入有效的位数')
      return
    }
    if (!batchShotForm.duration_frame || batchShotForm.duration_frame <= 0) {
      ElMessage.error('请输入有效的帧数')
      return
    }
    if (!batchShotForm.framepersecond || batchShotForm.framepersecond <= 0) {
      ElMessage.error('请输入有效的帧率')
      return
    }
    
    // 确保日期数据的正确性 - 处理批量表单
    const batchFormData = { ...batchShotForm }
    
    // 确保日期格式正确
    if (batchFormData.deadline) {
      // 验证日期格式
      if (typeof batchFormData.deadline === 'string') {
        const dateMatch = batchFormData.deadline.match(/^(\d{4})-(\d{2})-(\d{2})$/)
        if (dateMatch) {
          // 保持格式不变，但确保是合法日期
          const year = parseInt(dateMatch[1])
          const month = parseInt(dateMatch[2]) - 1 // JS月份从0开始
          const day = parseInt(dateMatch[3])
          
          const dateObj = new Date(year, month, day)
          if (
            dateObj.getFullYear() === year &&
            dateObj.getMonth() === month &&
            dateObj.getDate() === day
          ) {
            // 日期有效，重新格式化确保一致
            batchFormData.deadline = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
          } else {
            console.error('批量日期无效:', batchFormData.deadline)
            delete batchFormData.deadline
          }
        } else {
          console.error('批量日期格式错误:', batchFormData.deadline)
          delete batchFormData.deadline
        }
      } else if (batchFormData.deadline instanceof Date) {
        if (!isNaN(batchFormData.deadline.getTime())) {
          batchFormData.deadline = batchFormData.deadline.toISOString().split('T')[0]
        } else {
          console.error('批量日期对象无效:', batchFormData.deadline)
          delete batchFormData.deadline
        }
      } else {
        console.error('未知批量日期类型:', typeof batchFormData.deadline)
        delete batchFormData.deadline
      }
    }
    
    // 同样处理最近提交日期
    if (batchFormData.last_submit_date) {
      // 验证日期格式
      if (typeof batchFormData.last_submit_date === 'string') {
        const dateMatch = batchFormData.last_submit_date.match(/^(\d{4})-(\d{2})-(\d{2})$/)
        if (dateMatch) {
          // 保持格式不变，但确保是合法日期
          const year = parseInt(dateMatch[1])
          const month = parseInt(dateMatch[2]) - 1 // JS月份从0开始
          const day = parseInt(dateMatch[3])
          
          const dateObj = new Date(year, month, day)
          if (
            dateObj.getFullYear() === year &&
            dateObj.getMonth() === month &&
            dateObj.getDate() === day
          ) {
            // 日期有效，重新格式化确保一致
            batchFormData.last_submit_date = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
          } else {
            console.error('批量提交日期无效:', batchFormData.last_submit_date)
            delete batchFormData.last_submit_date
          }
        } else {
          console.error('批量提交日期格式错误:', batchFormData.last_submit_date)
          delete batchFormData.last_submit_date
        }
      } else if (batchFormData.last_submit_date instanceof Date) {
        if (!isNaN(batchFormData.last_submit_date.getTime())) {
          batchFormData.last_submit_date = batchFormData.last_submit_date.toISOString().split('T')[0]
        } else {
          console.error('批量提交日期对象无效:', batchFormData.last_submit_date)
          delete batchFormData.last_submit_date
        }
      } else {
        console.error('未知批量提交日期类型:', typeof batchFormData.last_submit_date)
        delete batchFormData.last_submit_date
      }
    }
    
    // 调试日期值
    console.log('批量表单提交前日期值:', {
      原始日期: batchShotForm.deadline,
      原始类型: typeof batchShotForm.deadline,
      处理后日期: batchFormData.deadline,
      处理后类型: typeof batchFormData.deadline,
      原始提交日期: batchShotForm.last_submit_date,
      原始提交类型: typeof batchShotForm.last_submit_date,
      处理后提交日期: batchFormData.last_submit_date,
      处理后提交类型: typeof batchFormData.last_submit_date
    })

    // 开始创建镜头
    loading.value = true
    try {
      // 构建批量添加的数据
      const batchData = {
        ...batchFormData,
        project: batchFormData.project,
        prefix: batchFormData.prefix,
        start: batchFormData.start_num,
        count: batchFormData.count,
        digit_count: batchFormData.digit_count
      }
      
      let successCount = 0
      let failCount = 0

      // 逐个创建镜头
      for (const shotName of batchShotNamePreview.value) {
        try {
          const shotData = {
            ...batchData,
            shot_code: shotName
          }
          
          const newShot = await shotStore.createShot(shotData)
          if (newShot) {
            successCount++
          } else {
            failCount++
          }
        } catch (error) {
          console.error(`创建镜头 ${shotName} 失败:`, error)
          failCount++
        }
      }

      // 显示结果
      if (successCount > 0) {
        ElMessage.success(`成功创建 ${successCount} 个镜头`)
      }
      if (failCount > 0) {
        ElMessage.warning(`有 ${failCount} 个镜头创建失败`)
      }

      await refreshShots()
    } catch (error) {
      console.error('批量创建镜头失败:', error)
      ElMessage.error('批量创建镜头失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
      // 清空表单并关闭对话框
      resetAddShotForms()
      addShotDialogVisible.value = false
    }
  } catch (error) {
    console.error('添加镜头失败:', error)
    ElMessage.error('添加镜头失败: ' + (error.message || '未知错误'))
  }
}

// 重置添加镜头表单
const resetAddShotForms = () => {
  // 重置单个添加表单
  Object.assign(singleShotForm, {
    project: selectedProject.value || '',
    shot_code: '',
    duration_frame: 24,
    framepersecond: 24,
    artist: '',
    prom_stage: 'LAY',
    deadline: '',
    last_submit_date: '',
    description: ''
  })
  
  // 重置批量添加表单
  Object.assign(batchShotForm, {
    project: selectedProject.value || '',
    prefix: 'SC_',
    start_num: 10,
    suffix: '',
    step: 10,
    count: 5,
    digit_count: 3,
    prom_stage: 'LAY',
    deadline: '',
    framepersecond: 24,
    duration_frame: 24,
    last_submit_date: '',
  })
}

// 页面导航
const goToHome = () => {
  router.push('/')
}

// 项目管理对话框
const projectManagementVisible = ref(false)

// 打开项目管理对话框
const openProjectManagement = () => {
  projectManagementVisible.value = true
}

// 处理项目刷新事件
const handleProjectRefresh = async () => {
  // 刷新项目列表
  await projectStore.fetchProjects()
  projects.value = projectStore.projects
  
  // 如果当前选择的项目被删除，则重置选择
  if (selectedProject.value && !projects.value.find(p => p.id === selectedProject.value)) {
    selectedProject.value = null
    ElMessage.info('当前选择的项目已被删除')
  }
  
  // 刷新镜头列表
  await refreshShots()
}

// 处理单个添加表单的日期
const handleSingleDeadlineChange = (val) => {
  console.log('单个截止日期变化:', val, typeof val)
  if (val) {
    if (typeof val === 'string') {
      if (/^\d{4}-\d{2}-\d{2}$/.test(val)) {
        singleShotForm.deadline = val
      } else {
        console.error('日期格式错误:', val)
        singleShotForm.deadline = null
      }
    } else if (val instanceof Date && !isNaN(val.getTime())) {
      singleShotForm.deadline = val.toISOString().split('T')[0]
    } else {
      console.error('未知日期格式:', val)
      singleShotForm.deadline = null
    }
    console.log('最终截止日期值:', singleShotForm.deadline)
  }
}

const handleSingleSubmitDateChange = (val) => {
  console.log('单个提交日期变化:', val, typeof val)
  if (val) {
    if (typeof val === 'string') {
      if (/^\d{4}-\d{2}-\d{2}$/.test(val)) {
        singleShotForm.last_submit_date = val
      } else {
        console.error('日期格式错误:', val)
        singleShotForm.last_submit_date = null
      }
    } else if (val instanceof Date && !isNaN(val.getTime())) {
      singleShotForm.last_submit_date = val.toISOString().split('T')[0]
    } else {
      console.error('未知日期格式:', val)
      singleShotForm.last_submit_date = null
    }
    console.log('最终提交日期值:', singleShotForm.last_submit_date)
  }
}

// 处理批量添加表单的日期
const handleBatchDeadlineChange = (val) => {
  console.log('批量截止日期变化:', val, typeof val)
  if (val) {
    if (typeof val === 'string') {
      if (/^\d{4}-\d{2}-\d{2}$/.test(val)) {
        batchShotForm.deadline = val
      } else {
        console.error('日期格式错误:', val)
        batchShotForm.deadline = null
      }
    } else if (val instanceof Date && !isNaN(val.getTime())) {
      batchShotForm.deadline = val.toISOString().split('T')[0]
    } else {
      console.error('未知日期格式:', val)
      batchShotForm.deadline = null
    }
    console.log('最终批量截止日期值:', batchShotForm.deadline)
  }
}

const handleBatchSubmitDateChange = (val) => {
  console.log('批量提交日期变化:', val, typeof val)
  if (val) {
    if (typeof val === 'string') {
      if (/^\d{4}-\d{2}-\d{2}$/.test(val)) {
        batchShotForm.last_submit_date = val
      } else {
        console.error('日期格式错误:', val)
        batchShotForm.last_submit_date = null
      }
    } else if (val instanceof Date && !isNaN(val.getTime())) {
      batchShotForm.last_submit_date = val.toISOString().split('T')[0]
    } else {
      console.error('未知日期格式:', val)
      batchShotForm.last_submit_date = null
    }
    console.log('最终批量提交日期值:', batchShotForm.last_submit_date)
  }
}
</script>

<style scoped>
.shot-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.shot-management-content {
  display: flex;
  height: calc(100vh - 20px);
  padding: 10px;
  gap: 10px;
  overflow: hidden;
}

.left-panel {
  flex: 3;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.right-panel {
  flex: 2;
  overflow: hidden;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.filters-container {
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 10px;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.home-button {
  margin-left: auto;
}

.page-title {
  font-size: 18px;
  margin: 0 0 10px 0;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.filter-item {
  width: 120px;
}

.search-input {
  width: 150px;
}

.shot-list-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.shot-list-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.shot-details-container {
  height: 100%;
  overflow-y: auto;
}

.empty-details {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-indicators {
  display: flex;
  flex-direction: row;
  gap: 2px;
  margin-left: 5px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.comment-indicator {
  background-color: #409EFF;
}

.note-indicator {
  background-color: #E6A23C;
}

.important-note-indicator {
  background-color: #F56C6C;
}

.text-danger {
  color: #F56C6C;
}

.text-warning {
  color: #E6A23C;
}

.pagination-container {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #f0f0f0;
  margin-top: 8px;
}

.selected-info {
  font-size: 12px;
  color: #606266;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.column-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* 添加以下新样式 */
.shot-code-container {
  display: flex;
  align-items: center;
}

/* 固定选择框列宽度 */
:deep(.el-table .el-table__cell.is-leaf.el-table-column--selection) {
  width: 40px !important;
}

:deep(.el-table-column--selection .cell) {
  min-width: 40px !important;
  max-width: 40px !important;
  padding-right: 10px;
  padding-left: 10px;
}

/* 添加镜头对话框相关样式 */
.batch-preview {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
  min-height: 80px;
  max-height: 120px;
}

.preview-title {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.preview-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.preview-tag {
  margin: 2px;
  flex: 0 0 calc(20% - 10px);
}

.preview-more {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  text-align: right;
}

.no-preview {
  color: #909399;
  text-align: center;
  padding: 20px 0;
  font-size: 14px;
}
</style> 