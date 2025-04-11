<template>
  <div class="shot-list-wrapper">
    <!-- 顶部过滤和操作栏 -->
    <div class="shot-list-toolbar">
      <div class="shot-filters">
        <!-- 项目筛选 -->
        <el-select 
          v-model="filters.project" 
          placeholder="选择项目" 
          clearable 
          @change="refreshShots"
        >
          <template v-if="projects && projects.length > 0">
            <el-option
              v-for="(project, index) in projects"
              :key="project?.id || index"
              :label="project?.name || '未命名项目'"
              :value="project?.id"
              v-if="project && project.id"
            />
          </template>
          <el-option v-else label="加载中..." :value="null" disabled />
        </el-select>
        
        <!-- 状态筛选 -->
        <el-select 
          v-model="filters.status" 
          placeholder="制作状态" 
          clearable 
          @change="refreshShots"
        >
          <el-option label="制作中" value="in_progress" />
          <el-option label="审核中" value="review" />
          <el-option label="已通过" value="approved" />
          <el-option label="需修改" value="need_revision" />
        </el-select>
        
        <!-- 推进阶段筛选 -->
        <el-select 
          v-model="filters.prom_stage" 
          placeholder="推进阶段" 
          clearable 
          @change="refreshShots"
        >
          <el-option label="布局" value="layout" />
          <el-option label="动画" value="animation" />
          <el-option label="灯光" value="lighting" />
          <el-option label="渲染" value="rendering" />
        </el-select>
        
        <!-- 制作者筛选 -->
        <el-select 
          v-model="filters.artist" 
          placeholder="制作者" 
          clearable 
          @change="refreshShots"
        >
          <template v-if="artists && artists.length > 0">
            <el-option
              v-for="(artist, index) in artists"
              :key="artist?.id || index"
              :label="artist?.username || '未知用户'"
              :value="artist?.id"
              v-if="artist && artist.id"
            />
          </template>
          <el-option v-else label="加载中..." :value="null" disabled />
        </el-select>
        
        <!-- 管理员和制片部门可见的部门筛选 -->
        <el-select 
          v-if="canFilterByDepartment"
          v-model="filters.department" 
          placeholder="部门" 
          clearable 
          @change="refreshShots"
        >
          <el-option label="动画" value="animation" />
          <el-option label="解算" value="fx" />
          <el-option label="后期" value="post" />
        </el-select>
        
        <!-- 搜索框 -->
        <el-input 
          v-model="filters.search" 
          placeholder="搜索镜头号或描述"
          clearable
          @input="debounceSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- 表格操作区 -->
      <div class="shot-operations">
        <!-- 添加项目按钮 -->
        <el-button type="success" @click="openAddProjectDialog">
          <el-icon><Plus /></el-icon>添加项目
        </el-button>
        
        <!-- 添加镜头按钮 -->
        <el-button type="success" @click="openAddShotDialog">
          <el-icon><Plus /></el-icon>添加镜头
        </el-button>
        
        <!-- 自定义列显示 -->
        <el-dropdown @command="toggleColumnVisibility" trigger="click">
          <el-button type="primary" plain>
            自定义列
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="shot_code">
                <el-checkbox :modelValue="isColumnVisible('shot_code')">镜头号</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="prom_stage">
                <el-checkbox :modelValue="isColumnVisible('prom_stage')">推进阶段</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="status">
                <el-checkbox :modelValue="isColumnVisible('status')">制作状态</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="artist_name">
                <el-checkbox :modelValue="isColumnVisible('artist_name')">制作者</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="duration_frame">
                <el-checkbox :modelValue="isColumnVisible('duration_frame')">帧数</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="deadline">
                <el-checkbox :modelValue="isColumnVisible('deadline')">截止日期</el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item command="last_submit_date">
                <el-checkbox :modelValue="isColumnVisible('last_submit_date')">最近提交日期</el-checkbox>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 批量操作按钮 -->
        <el-dropdown @command="handleBatchOperation" :disabled="!hasSelection">
          <el-button type="primary" :disabled="!hasSelection">
            批量操作
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="rename">批量重命名</el-dropdown-item>
              <el-dropdown-item command="update-status">修改状态</el-dropdown-item>
              <el-dropdown-item command="update-stage">修改推进阶段</el-dropdown-item>
              <el-dropdown-item command="update-artist">修改制作者</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 刷新按钮 -->
        <el-button @click="refreshShots" :loading="loading">
          <el-icon><refresh /></el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 镜头数据表格 -->
    <el-table
      ref="shotTableRef"
      v-loading="loading"
      :data="Array.isArray(shots) ? shots : []"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      @row-click="handleRowClick"
      height="calc(100vh - 230px)"
      :row-class-name="getRowClass"
    >
      <el-table-column
        type="selection"
        width="50"
      />
      <el-table-column 
        v-if="isColumnVisible('shot_code')"
        prop="shot_code" 
        label="镜头号" 
        sortable
        min-width="180"
      />
      <el-table-column 
        v-if="isColumnVisible('prom_stage')"
        prop="prom_stage" 
        label="推进阶段" 
        sortable
        min-width="120"
      />
      <el-table-column 
        v-if="isColumnVisible('status')"
        prop="status" 
        label="制作状态" 
        sortable
        min-width="120"
      >
        <template #default="scope">
          <el-tag :type="getStatusTagType(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column 
        v-if="isColumnVisible('artist_name')"
        prop="artist_name" 
        label="制作者" 
        min-width="120"
      />
      <el-table-column 
        v-if="isColumnVisible('duration_frame')"
        prop="duration_frame" 
        label="帧数" 
        sortable
        min-width="100"
      />
      <el-table-column 
        v-if="isColumnVisible('deadline')"
        prop="deadline" 
        label="截止日期" 
        sortable
        min-width="120"
      >
        <template #default="scope">
          <span :class="getDeadlineClass(scope.row)">
            {{ scope.row.deadline }}
          </span>
        </template>
      </el-table-column>
      <el-table-column 
        v-if="isColumnVisible('last_submit_date')"
        prop="last_submit_date" 
        label="最近提交日期" 
        sortable
        min-width="120"
      />
    </el-table>
    
    <!-- 分页器 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.limit"
        :page-sizes="[20, 50, 100, 200]"
        :total="totalShots"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 批量重命名弹窗 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="批量重命名镜头"
      width="500px"
    >
      <el-form 
        :model="renameForm" 
        label-width="120px"
        :rules="renameRules"
        ref="renameFormRef"
      >
        <el-form-item label="前缀" prop="prefix">
          <el-input v-model="renameForm.prefix" placeholder="例如: DH_EP001_SC001_Shot" />
        </el-form-item>
        <el-form-item label="后缀" prop="suffix">
          <el-input v-model="renameForm.suffix" placeholder="可选" />
        </el-form-item>
        <el-form-item label="起始编号" prop="start_number">
          <el-input-number v-model="renameForm.start_number" :min="1" />
        </el-form-item>
        <el-form-item label="结束编号" prop="end_number">
          <el-input-number 
            v-model="renameForm.end_number" 
            :min="renameForm.start_number + 1"
            :disabled="!!renameForm.count"
          />
          <div class="form-item-tip">与序列数二选一</div>
        </el-form-item>
        <el-form-item label="序列数量" prop="count">
          <el-input-number 
            v-model="renameForm.count" 
            :min="1"
            :disabled="!!renameForm.end_number"
          />
          <div class="form-item-tip">与结束编号二选一</div>
        </el-form-item>
        <el-form-item label="步长" prop="step">
          <el-input-number v-model="renameForm.step" :min="1" />
        </el-form-item>
        <el-form-item label="数字位数" prop="digits">
          <el-input-number v-model="renameForm.digits" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRename" :loading="loading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量更新状态弹窗 -->
    <el-dialog
      v-model="updateStatusDialogVisible"
      title="批量更新状态"
      width="400px"
    >
      <el-form 
        :model="updateForm" 
        label-width="100px"
      >
        <el-form-item label="制作状态">
          <el-select v-model="updateForm.status" placeholder="选择状态">
            <el-option label="制作中" value="in_progress" />
            <el-option label="审核中" value="review" />
            <el-option label="已通过" value="approved" />
            <el-option label="需修改" value="need_revision" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateStatusDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpdateStatus" :loading="loading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量更新推进阶段弹窗 -->
    <el-dialog
      v-model="updateStageDialogVisible"
      title="批量更新推进阶段"
      width="400px"
    >
      <el-form 
        :model="updateForm" 
        label-width="100px"
      >
        <el-form-item label="推进阶段">
          <el-select v-model="updateForm.prom_stage" placeholder="选择推进阶段">
            <el-option label="布局" value="layout" />
            <el-option label="动画" value="animation" />
            <el-option label="灯光" value="lighting" />
            <el-option label="渲染" value="rendering" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateStageDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpdateStage" :loading="loading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 批量更新制作者弹窗 -->
    <el-dialog
      v-model="updateArtistDialogVisible"
      title="批量更新制作者"
      width="400px"
    >
      <el-form 
        :model="updateForm" 
        label-width="100px"
      >
        <el-form-item label="制作者">
          <el-select v-model="updateForm.artist_id" placeholder="选择制作者">
            <el-option
              v-for="artist in artists"
              :key="artist.id"
              :label="artist.username"
              :value="artist.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="updateArtistDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitUpdateArtist" :loading="loading">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加项目弹窗 -->
    <el-dialog
      v-model="addProjectDialogVisible"
      title="添加新项目"
      width="500px"
    >
      <el-form 
        :model="projectForm" 
        label-width="120px"
        :rules="projectRules"
        ref="projectFormRef"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        
        <el-form-item label="项目代号" prop="code">
          <el-input v-model="projectForm.code" placeholder="例如：HHN-01" />
        </el-form-item>
        
        <el-form-item label="项目状态" prop="status">
          <el-select v-model="projectForm.status" placeholder="请选择项目状态">
            <el-option label="进行中" value="active" />
            <el-option label="规划中" value="planning" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="projectForm.start_date" type="date" placeholder="选择开始日期" />
        </el-form-item>
        
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker v-model="projectForm.end_date" type="date" placeholder="选择结束日期" />
        </el-form-item>
        
        <el-form-item label="项目描述" prop="description">
          <el-input v-model="projectForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addProjectDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitProjectForm" :loading="projectSubmitting">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加镜头弹窗 -->
    <el-dialog
      v-model="addShotDialogVisible"
      title="添加新镜头"
      width="500px"
    >
      <el-form 
        :model="shotForm" 
        label-width="120px"
        :rules="shotRules"
        ref="shotFormRef"
      >
        <el-form-item label="所属项目" prop="project">
          <el-select 
            v-model="shotForm.project" 
            placeholder="请选择项目" 
            filterable
          >
            <template v-if="projects && projects.length > 0">
              <el-option
                v-for="project in projects"
                :key="project.id || 0"
                :label="project?.name || '未命名项目'"
                :value="project?.id"
                v-if="project && project.id"
              />
            </template>
            <el-option v-else label="加载中..." :value="null" disabled />
          </el-select>
        </el-form-item>
        
        <el-form-item label="镜头编号" prop="shot_code">
          <el-input v-model="shotForm.shot_code" placeholder="例如：DH_001, JS_002, HQ_003" />
        </el-form-item>
        
        <el-form-item label="制作状态" prop="status">
          <el-select v-model="shotForm.status" placeholder="请选择制作状态">
            <el-option label="制作中" value="in_progress" />
            <el-option label="审核中" value="review" />
            <el-option label="已通过" value="approved" />
            <el-option label="需修改" value="need_revision" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="推进阶段" prop="prom_stage">
          <el-input v-model="shotForm.prom_stage" placeholder="例如：layout, animation, lighting" />
        </el-form-item>
        
        <el-form-item label="截止日期" prop="deadline">
          <el-date-picker v-model="shotForm.deadline" type="date" placeholder="选择截止日期" />
        </el-form-item>
        
        <el-form-item label="帧数" prop="duration_frame">
          <el-input-number v-model="shotForm.duration_frame" :min="0" />
        </el-form-item>
        
        <el-form-item label="制作者" prop="artist">
          <el-select v-model="shotForm.artist" placeholder="请选择制作者" filterable clearable>
            <template v-if="artists && artists.length > 0">
              <el-option
                v-for="artist in artists"
                :key="artist.id || 0"
                :label="artist?.username || '未知用户'"
                :value="artist?.id"
                v-if="artist && artist.id"
              />
            </template>
            <el-option v-else label="加载中..." :value="null" disabled />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="shotForm.description" type="textarea" :rows="3" placeholder="请输入镜头描述" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addShotDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitShotForm" :loading="shotSubmitting">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useShotStore } from '@/stores/shotStore';
import { useProjectStore } from '@/stores/projectStore';
import { useUserStore } from '@/stores/userStore';
import { Search, ArrowDown, Refresh, Plus } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { debounce } from 'lodash-es';

// 组件 emit
const emit = defineEmits(['shot-selected']);

// 响应式搜索
const debounceSearch = debounce(() => {
  refreshShots();
}, 500);

// 引入状态仓库
const shotStore = useShotStore();
const projectStore = useProjectStore();
const userStore = useUserStore();

// 从状态仓库获取数据和方法
const shots = ref(shotStore.shots);
const loading = ref(false);
const filters = ref({
  project: null,
  status: null,
  prom_stage: null,
  artist: null,
  department: null,
  search: ''
});
const pagination = ref(shotStore.pagination);
const totalShots = computed(() => shotStore.totalShots);
const selectedShotIds = computed(() => shotStore.selectedShotIds);
const canFilterByDepartment = computed(() => shotStore.canFilterByDepartment);
const visibleColumns = ref(shotStore.visibleColumns);

// 本地状态
const shotTableRef = ref(null);
const hasSelection = computed(() => selectedShotIds.value.length > 0);
const renameDialogVisible = ref(false);
const updateStatusDialogVisible = ref(false);
const updateStageDialogVisible = ref(false);
const updateArtistDialogVisible = ref(false);
const addProjectDialogVisible = ref(false);
const addShotDialogVisible = ref(false);
const projectSubmitting = ref(false);
const shotSubmitting = ref(false);

// 项目和艺术家列表
const projects = ref([]);
const artists = ref([]);

// 确保Vue实例创建后立即初始化这些变量
// 防止"property was accessed during render but is not defined on instance"错误
onMounted(() => {
  if (!projects.value) projects.value = [];
  if (!artists.value) artists.value = [];
});

// 重命名表单
const renameFormRef = ref(null);
const renameForm = ref({
  prefix: '',
  suffix: '',
  start_number: 10,
  end_number: null,
  count: null,
  step: 10,
  digits: 4
});

// 更新表单
const updateForm = ref({
  status: '',
  prom_stage: '',
  artist_id: null
});

// 重命名表单验证规则
const renameRules = {
  prefix: [
    { required: true, message: '请输入前缀', trigger: 'blur' }
  ],
  start_number: [
    { required: true, message: '请输入起始编号', trigger: 'blur' }
  ]
};

// 项目表单
const projectFormRef = ref(null);
const projectForm = ref({
  name: '',
  code: '',
  status: 'active',
  start_date: '',
  end_date: '',
  description: ''
});

// 项目表单验证规则
const projectRules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入项目代号', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'blur' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'blur' }
  ]
};

// 镜头表单
const shotFormRef = ref(null);
const shotForm = ref({
  project: '',
  shot_code: '',
  status: 'in_progress',
  prom_stage: '',
  deadline: '',
  duration_frame: 0,
  artist: '',
  description: ''
});

// 镜头表单验证规则
const shotRules = {
  project: [
    { required: true, message: '请选择所属项目', trigger: 'blur' }
  ],
  shot_code: [
    { required: true, message: '请输入镜头编号', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择制作状态', trigger: 'blur' }
  ],
  prom_stage: [
    { required: true, message: '请输入推进阶段', trigger: 'blur' }
  ],
  deadline: [
    { required: true, message: '请选择截止日期', trigger: 'blur' }
  ],
  duration_frame: [
    { required: true, message: '请输入帧数', trigger: 'blur' }
  ],
  artist: []
};

// 初始化数据
onMounted(async () => {
  // 同步filters与store
  if (shotStore.filters) {
    filters.value = { ...shotStore.filters };
  }
  
  await Promise.all([
    fetchProjects(),
    fetchArtists(),
    refreshShots()
  ]);
});

// 监听过滤条件变化
watch(() => filters.value.search, debounceSearch);

// 监听store中filters变化
watch(() => shotStore.filters, (newFilters) => {
  if (newFilters) {
    filters.value = { ...newFilters };
  }
}, { deep: true });

// 本地filters变化时同步到store
watch(filters, (newFilters) => {
  shotStore.filters = { ...newFilters };
}, { deep: true });

// 获取项目列表
async function fetchProjects() {
  try {
    loading.value = true;
    const response = await projectStore.getProjects();
    projects.value = response?.data || [];
    console.log('ShotList.vue:724 项目列表加载成功，共', projects.value.length, '个项目');
    return projects.value;
  } catch (error) {
    console.error('获取项目列表失败:', error);
    ElMessage.error('获取项目列表失败: ' + (error.message || '未知错误'));
    projects.value = [];
    return [];
  } finally {
    loading.value = false;
  }
}

// 获取艺术家列表
async function fetchArtists() {
  try {
    const response = await userStore.getArtists();
    artists.value = response?.data || [];
    return artists.value;
  } catch (error) {
    console.error('获取艺术家列表失败:', error);
    ElMessage.error('获取艺术家列表失败: ' + (error.message || '未知错误'));
    artists.value = [];
    return [];
  }
}

// 刷新镜头列表
async function refreshShots() {
  try {
    loading.value = true;
    await shotStore.fetchShots({
      ...filters.value,
      page: pagination.value.page,
      limit: pagination.value.limit
    });
  } catch (error) {
    console.error('获取镜头列表失败:', error);
    ElMessage.error('获取镜头列表失败');
  } finally {
    loading.value = false;
  }
}

// 处理表格行点击
function handleRowClick(row) {
  // 发射事件通知父组件显示详情
  emit('shot-selected', row.id);
}

// 处理表格选择变化
function handleSelectionChange(selection) {
  shotStore.selectedShotIds = selection.map(item => item.id);
}

// 处理分页大小变化
function handleSizeChange(size) {
  pagination.value.limit = size;
  refreshShots();
}

// 处理页码变化
function handleCurrentChange(page) {
  pagination.value.page = page;
  refreshShots();
}

// 处理批量操作
function handleBatchOperation(command) {
  if (command === 'rename') {
    renameDialogVisible.value = true;
  } else if (command === 'update-status') {
    updateStatusDialogVisible.value = true;
  } else if (command === 'update-stage') {
    updateStageDialogVisible.value = true;
  } else if (command === 'update-artist') {
    updateArtistDialogVisible.value = true;
  }
}

// 提交重命名
async function submitRename() {
  if (!renameFormRef.value) return;
  
  try {
    await renameFormRef.value.validate();
    
    const { count, end_number } = renameForm.value;
    if (!count && !end_number) {
      ElMessage.warning('请提供结束编号或序列数量其中之一');
      return;
    }
    
    // 确认对话框
    await ElMessageBox.confirm(
      `确定要批量重命名${selectedShotIds.value.length}个镜头吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const response = await shotStore.bulkRenameShots(renameForm.value);
    
    ElMessage.success('镜头重命名成功');
    
    // 如果API返回警告信息，显示给用户
    if (response.warning) {
      ElMessage.warning(response.warning);
    }
    
    renameDialogVisible.value = false;
  } catch (error) {
    if (error === 'cancel') return;
    console.error('重命名错误:', error);
    ElMessage.error('重命名失败: ' + (error.message || '未知错误'));
  }
}

// 提交更新状态
async function submitUpdateStatus() {
  try {
    if (!updateForm.value.status) {
      ElMessage.warning('请选择制作状态');
      return;
    }
    
    await ElMessageBox.confirm(
      `确定要将${selectedShotIds.value.length}个镜头的状态更新为"${getStatusText(updateForm.value.status)}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await shotStore.bulkUpdateShots({ status: updateForm.value.status });
    
    ElMessage.success('状态更新成功');
    updateStatusDialogVisible.value = false;
    updateForm.value.status = '';
  } catch (error) {
    if (error === 'cancel') return;
    console.error('更新状态错误:', error);
    ElMessage.error('更新状态失败: ' + (error.message || '未知错误'));
  }
}

// 提交更新推进阶段
async function submitUpdateStage() {
  try {
    if (!updateForm.value.prom_stage) {
      ElMessage.warning('请选择推进阶段');
      return;
    }
    
    await ElMessageBox.confirm(
      `确定要将${selectedShotIds.value.length}个镜头的推进阶段更新为"${updateForm.value.prom_stage}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await shotStore.bulkUpdateShots({ prom_stage: updateForm.value.prom_stage });
    
    ElMessage.success('推进阶段更新成功');
    updateStageDialogVisible.value = false;
    updateForm.value.prom_stage = '';
  } catch (error) {
    if (error === 'cancel') return;
    console.error('更新推进阶段错误:', error);
    ElMessage.error('更新推进阶段失败: ' + (error.message || '未知错误'));
  }
}

// 提交更新制作者
async function submitUpdateArtist() {
  try {
    if (!updateForm.value.artist_id) {
      ElMessage.warning('请选择制作者');
      return;
    }
    
    await ElMessageBox.confirm(
      `确定要将${selectedShotIds.value.length}个镜头的制作者更新为"${artists.value.find(a => a.id === updateForm.value.artist_id)?.username}"吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await shotStore.bulkUpdateShots({ artist_id: updateForm.value.artist_id });
    
    ElMessage.success('制作者更新成功');
    updateArtistDialogVisible.value = false;
    updateForm.value.artist_id = null;
  } catch (error) {
    if (error === 'cancel') return;
    console.error('更新制作者错误:', error);
    ElMessage.error('更新制作者失败: ' + (error.message || '未知错误'));
  }
}

// 添加新项目
async function submitProjectForm() {
  if (!projectFormRef.value) return;
  
  try {
    await projectFormRef.value.validate();
    
    await projectStore.addProject(projectForm.value);
    
    ElMessage.success('新项目添加成功');
    addProjectDialogVisible.value = false;
    projectForm.value = {
      name: '',
      code: '',
      status: 'active',
      start_date: '',
      end_date: '',
      description: ''
    };
  } catch (error) {
    console.error('添加项目失败:', error);
    ElMessage.error('添加项目失败: ' + (error.message || '未知错误'));
  }
}

// 添加新镜头
async function submitShotForm() {
  if (!shotFormRef.value) return;
  
  try {
    shotSubmitting.value = true;
    await shotFormRef.value.validate();
    
    // 确保表单中的project和artist字段有效
    if (!shotForm.value.project) {
      ElMessage.warning('请选择所属项目');
      return;
    }
    
    await shotStore.addShot(shotForm.value);
    
    ElMessage.success('新镜头添加成功');
    addShotDialogVisible.value = false;
    shotForm.value = {
      project: '',
      shot_code: '',
      status: 'in_progress',
      prom_stage: '',
      deadline: '',
      duration_frame: 0,
      artist: null,
      description: ''
    };
    
    // 刷新镜头列表
    await refreshShots();
  } catch (error) {
    console.error('添加镜头失败:', error);
    ElMessage.error('添加镜头失败: ' + (error.message || '未知错误'));
  } finally {
    shotSubmitting.value = false;
  }
}

// 打开添加镜头对话框
function openAddShotDialog() {
  // 先确保项目列表已加载
  if (!projects.value || projects.value.length === 0) {
    fetchProjects()
      .then(() => {
        if (projects.value && projects.value.length > 0) {
          initShotForm();
        } else {
          ElMessage.warning('没有可用的项目，请先创建项目');
        }
      })
      .catch(error => {
        console.error('获取项目列表失败:', error);
        ElMessage.error('获取项目列表失败，请稍后再试');
      });
  } else {
    initShotForm();
  }
}

// 初始化镜头表单
function initShotForm() {
  // 获取当前项目ID
  const defaultProject = filters.value.project || 
    (projects.value && projects.value.length > 0 && projects.value[0] && projects.value[0].id) || 
    '';
  
  // 清空并重新初始化所有属性
  shotForm.value = {
    project: defaultProject,
    shot_code: '',
    status: 'in_progress',
    prom_stage: 'layout',  // 设置默认值
    deadline: new Date(new Date().setMonth(new Date().getMonth() + 1)),
    duration_frame: 100,
    artist: null,  // 确保使用null而不是空字符串
    description: ''
  };
  
  // 确保有项目和艺术家数据
  if (!artists.value || artists.value.length === 0) {
    fetchArtists().catch(error => {
      console.error('获取艺术家列表失败:', error);
    });
  }
  
  if (!projects.value || projects.value.length === 0) {
    fetchProjects().catch(error => {
      console.error('获取项目列表失败:', error);
    });
  }
  
  addShotDialogVisible.value = true;
}

// 获取状态文本
function getStatusText(status) {
  return shotStore.getStatusText(status);
}

// 获取状态标签类型
function getStatusTagType(status) {
  const typeMap = {
    'in_progress': '',
    'review': 'warning',
    'approved': 'success',
    'need_revision': 'danger'
  };
  return typeMap[status] || '';
}

// 判断列是否可见
function isColumnVisible(columnName) {
  return visibleColumns.value.includes(columnName);
}

// 切换列可见性
function toggleColumnVisibility(columnName) {
  const index = visibleColumns.value.indexOf(columnName);
  if (index !== -1) {
    visibleColumns.value.splice(index, 1);
  } else {
    visibleColumns.value.push(columnName);
  }
}

// 获取截止日期样式类
function getDeadlineClass(row) {
  const deadline = new Date(row.deadline);
  const today = new Date();
  const diffTime = Math.abs(deadline - today);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return 'deadline-overdue';
  } else if (diffDays < 7) {
    return 'deadline-approaching';
  } else {
    return '';
  }
}

// 获取行样式类
function getRowClass({ row }) {
  if (!row) return '';
  
  if (row.status === 'need_revision') {
    return 'shot-row-need-revision';
  } else if (row.status === 'approved') {
    return 'shot-row-approved';
  }
  return '';
}

// 打开添加项目对话框
function openAddProjectDialog() {
  projectForm.value = {
    name: '',
    code: '',
    status: 'active',
    start_date: new Date(),
    end_date: new Date(new Date().setMonth(new Date().getMonth() + 6)),
    description: ''
  };
  addProjectDialogVisible.value = true;
}
</script>

<style scoped>
.shot-list-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.shot-list-toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  gap: 16px;
  flex-wrap: wrap;
}

.shot-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
}

.shot-operations {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.deadline-expired, .deadline-overdue {
  color: #F56C6C;
  font-weight: bold;
}

.deadline-late {
  color: #E6A23C;
  font-weight: bold;
}

.deadline-approaching {
  color: #E6A23C;
}

.shot-row-need-revision {
  background-color: rgba(245, 108, 108, 0.1);
}

.shot-row-approved {
  background-color: rgba(103, 194, 58, 0.1);
}

.form-item-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
