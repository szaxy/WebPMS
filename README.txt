荷和年动画项目管理平台开发文档  
版本: 1.0 (MVP阶段)  
技术栈: Django 4.x + Vue3 + PostgreSQL + Docker  

---

注意：CGTeamwork 连接功能的开发暂停，先开发其他功能。

一、架构设计  
1. 整体架构  
前端Vue3通过Axios调用Django REST Framework接口，后端连接PostgreSQL数据库、Redis缓存、CGTeamwork API和AIMS服务。  

2. 技术栈分工  
- 前端层：Vue3 + Pinia + Vite，负责状态看板/反馈系统/数据可视化  
- 后端层：Django + DRF + Celery，处理REST API/权限控制/CGTeamwork同步任务  
- 数据库层：PostgreSQL + pgAdmin，负责结构化数据存储  
- 运维层：Docker + Nginx + Gunicorn，实现容器化部署/负载均衡  

---

二、开发流程  
1. 环境搭建 (Day 1-3)  
使用Docker构建开发环境，包含：  
- docker-compose.yml  
- backend目录（Django项目）  
- frontend目录（Vue项目）  
- db目录（PostgreSQL初始化脚本）  

2. 数据库设计  
核心表结构设计：

1. User (用户表)
   - id: 主键
   - username: 用户名
   - email: 邮箱
   - role: 角色(管理员/制作人/艺术家)
   - department: 部门
   - cgtw_id: CGTeamwork用户ID

2. Project (项目表)
   - id: 主键
   - name: 项目名称
   - code: 项目代号
   - status: 项目状态
   - start_date: 开始日期
   - end_date: 结束日期
   - description: 项目描述
   - cgtw_project_id: CGTeamwork项目ID

3. Shot (镜头表)
   - id: 主键
   - project: 外键(Project)
   - shot_code: 镜头编号
   - status: 制作状态
   - deadline: 截止日期
   - duration: 时长(秒)
   - description: 描述
   - metadata: JSON字段
   - cgtw_task_id: CGTeamwork任务ID
   - created_at: 创建时间
   - updated_at: 更新时间

4. Comment (反馈表)
   - id: 主键
   - shot: 外键(Shot)
   - user: 外键(User)
   - content: 反馈内容
   - timestamp: 时间戳
   - is_resolved: 是否已解决
   - reply_to: 外键(Comment,可空)

5. Attachment (附件表)
   - id: 主键
   - comment: 外键(Comment)
   - file_path: 文件路径
   - file_name: 文件名
   - file_size: 文件大小
   - mime_type: 文件类型

6. UserMention (用户提及表)
   - id: 主键
   - comment: 外键(Comment)
   - user: 外键(User)
   - is_read: 是否已读

7. SyncLog (同步日志表)
   - id: 主键
   - sync_type: 同步类型
   - start_time: 开始时间
   - end_time: 结束时间
   - status: 同步状态
   - error_message: 错误信息
   - items_synced: 同步条目数

3. API设计规范  
镜头列表接口示例：  
- 请求方式：GET  
- 权限控制：需登录认证  
- 返回字段：id、shot_code、status、updated_at  
- 序列化器：ShotSerializer控制字段读写权限  

4. 前端核心模块  
状态看板实现方案：  
- 使用Vue3组合式API + draggable组件实现拖拽交互  
- 按状态分类显示镜头卡片（制作中/已审核/需修改）  
- 拖拽结束时触发PATCH请求更新镜头状态  
- 通过useFetch实时获取镜头数据  

---

三、关键模块实现细节  
1. CGTeamwork同步模块  
同步策略：  
- 每日凌晨1点执行Celery定时任务  
- 使用CGTeamwork官方API获取增量数据  
- 通过update_or_create方法同步到本地数据库  
- 记录最后同步时间用于增量更新  

异常处理方案：  
- 配置Celery自动重试机制（3次）  
- 单独建立同步日志表记录操作详情  
- 同步失败时发送邮件通知管理员  

2. 实时状态更新  
技术方案：Django Channels实现WebSocket通信  
- 建立项目专属通信频道  
- 用户连接时加入对应项目组  
- 状态变更时广播消息到组内所有成员  
- 前端监听消息实时更新看板  

---

四、注意事项与最佳实践  
1. 性能优化  
数据库优化：  
- 为shot_code和status字段创建联合索引  
- 使用django-debug-toolbar分析慢查询  
- 分页查询默认限制100条/页  

缓存策略：  
- 对频繁访问的API添加15分钟缓存  
- 使用Redis缓存热点数据  

2. 安全措施  
认证机制：  
- 采用JWT认证（2小时访问令牌+7天刷新令牌）  
- 密钥通过环境变量注入  

API防护：  
- 启用CORS白名单限制跨域请求  
- 配置接口访问频率限制  
- 记录敏感操作审计日志  

3. 兼容性要求  
- 支持CGTeamwork v7.2+版本API  
- 适配Chrome/Firefox/Edge最新两个版本  
- 移动端响应式布局支持  

---

五、测试计划  
1. 测试类型  
- 单元测试：使用pytest覆盖80%以上代码  
- API测试：Postman编写完整接口测试用例  
- E2E测试：Cypress验证核心用户流程  
- 压力测试：Locust模拟500并发场景  

2. 典型测试场景（状态更新）  
测试步骤：  
1) 建立WebSocket连接  
2) 拖拽镜头到"已审核"列  
3) 验证：  
   - 数据库状态字段更新  
   - WebSocket接收广播消息  
   - 前端看板实时刷新  

---

六、部署方案  
1. 服务器配置建议  
开发环境：2核CPU/4GB内存/50GB SSD  
生产环境：4核CPU/16GB内存/200GB SSD+备份  

2. 持续集成流程  
- 代码提交触发单元测试  
- 测试通过后构建Docker镜像  
- 生产环境使用Ansible自动部署  

---

七、风险管理  
1. CGTeamwork API变动  
应对方案：  
- 封装独立适配层隔离业务逻辑  
- 每日执行接口健康检查  

2. 大文件上传问题  
应对方案：  
- 实现分块上传功能  
- 支持上传断点续传  

3. 实时性不足  
应对方案：  
- 降级使用30秒短轮询  
- 优化数据库查询性能  

---

关键实施路径建议：  
1. 优先完成用户认证系统搭建  
2. 实现镜头基础CRUD功能  
3. 验证CGTeamwork单向数据同步  
建议采用敏捷开发模式，每周进行代码审查和进度同步。


开发流程（具体版）

# 荷和年动画项目管理平台开发文档分析与优化

## 文档分析

### 合理性分析
1. **技术栈选择合理**：Django+Vue3+PostgreSQL组合稳定可靠，适合中型项目
2. **架构设计清晰**：前后端分离架构符合现代开发趋势
3. **关键功能完备**：CGTeamwork同步、实时状态更新等核心功能已规划
4. **安全性考虑充分**：JWT认证、CORS白名单等安全措施已纳入

### 可优化点
1. **数据模型不完整**：仅提及两个表，缺少完整的实体关系设计
2. **接口定义不详细**：未提供完整的API列表和参数规范
3. **前端UI/UX规范缺失**：未明确设计语言和交互规范
4. **项目管理计划模糊**：缺少具体时间线和资源分配
5. **错误处理机制不足**：未详细说明全局异常处理策略
6. **DevOps流程不完整**：CI/CD流程描述简略

## 优化后的开发步骤详细文档

### 一、项目启动与规划 (1周)

#### 1.1 需求细化与分析
- 收集用户故事和功能需求
- 确定MVP核心功能清单
- 建立功能优先级矩阵

#### 1.2 技术架构设计
- **后端架构**：
  - Django 4.x + DRF
  - Celery + Redis (异步任务)
  - PostgreSQL (主数据库)
  - Django Channels (WebSocket)
  
- **前端架构**：
  - Vue 3 + Pinia
  - Vite (构建工具)
  - Element Plus (UI组件库)
  - Axios (HTTP请求)
  - Pinia (状态管理)
  - Vue-Router (路由管理)

#### 1.3 详细的数据库设计
```
核心表结构设计：

1. User (用户表)
   - id: 主键
   - username: 用户名
   - email: 邮箱
   - role: 角色(系统管理员/管理/艺术家)
   - department: 部门（动画/后期/解算/制片）
   - cgtw_id: CGTeamwork用户ID

2. Project (项目表)
   - id: 主键
   - name: 项目名称
   - code: 项目代号
   - status: 项目状态（进行中/已暂停/已归档）
   - start_date: 开始日期
   - recsubmit_date: 最近提交日期
   - end_date: 结束日期
   - description: 项目描述
   - cgtw_project_id: CGTeamwork项目ID

3. Shot (镜头表)
   - id: 主键
   - project: 外键(Project)
   - shot_code: 镜头编号
   - prom_stage: 推进阶段
   - status: 制作状态
   - deadline: 截止日期
   - duration_frame: 时长(帧)
   - description: 描述
   - metadata: JSON字段
   - cgtw_task_id: CGTeamwork任务ID
   - created_at: 创建时间
   - updated_at: 更新时间

4. Comment (反馈表)
   - id: 主键
   - shot: 外键(Shot)
   - user: 外键(User)
   - content: 反馈内容
   - timestamp: 时间戳
   - is_resolved: 是否已解决
   - reply_to: 外键(Comment,可空)

5. Attachment (附件表)
   - id: 主键
   - comment: 外键(Comment)
   - file_path: 文件路径
   - file_name: 文件名
   - file_size: 文件大小
   - mime_type: 文件类型

6. UserMention (用户提及表)
   - id: 主键
   - comment: 外键(Comment)
   - user: 外键(User)
   - is_read: 是否已读

7. SyncLog (同步日志表)
   - id: 主键
   - sync_type: 同步类型
   - start_time: 开始时间
   - end_time: 结束时间
   - status: 同步状态
   - error_message: 错误信息
   - items_synced: 同步条目数
```

#### 1.4 项目时间线与里程碑
- 第1-2周：环境搭建与数据库实现
- 第3-4周：用户认证与基础API开发
- 第5-7周：CGTeamwork同步模块开发
- 第8-10周：前端看板与反馈系统实现
- 第11-12周：测试、修复与优化

### 二、开发环境搭建 (3天)

#### 2.1 Docker容器配置
```yaml
# docker-compose.yml核心配置
version: '3'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file: .env
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    env_file: .env
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"

  celery:
    build: ./backend
    command: celery -A core worker -l INFO
    volumes:
      - ./backend:/app
    env_file: .env
    depends_on:
      - backend
      - redis

  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

#### 2.2 前后端项目初始化
- 后端Django项目结构:
  ```
  backend/
  ├── core/             # 项目核心配置
  ├── users/            # 用户认证模块
  ├── projects/         # 项目管理模块  
  ├── shots/            # 镜头管理模块
  ├── comments/         # 反馈系统模块
  ├── integrations/     # 第三方集成模块
  │   └── cgtw/         # CGTeamwork集成
  ├── utils/            # 通用工具函数
  └── tests/            # 测试目录
  ```

- 前端Vue项目结构:
  ```
  frontend/
  ├── src/
  │   ├── assets/       # 静态资源
  │   ├── components/   # 公共组件
  │   ├── layouts/      # 布局组件
  │   ├── router/       # 路由配置
  │   ├── stores/       # Pinia状态
  │   ├── views/        # 页面组件
  │   │   ├── dashboard/
  │   │   ├── shots/
  │   │   ├── comments/
  │   │   └── settings/
  │   ├── services/     # API服务
  │   └── utils/        # 工具函数
  └── tests/            # 测试目录
  ```

### 三、后端开发 (4周)

#### 3.1 用户认证系统
- 实现JWT认证机制
- 创建用户权限系统(RBAC模型)
- 集成CGTeamwork用户同步

#### 3.2 核心API开发
详细的API端点设计：

```
1. 用户相关API
   - POST /api/auth/login/            # 用户登录
   - POST /api/auth/refresh/          # 刷新令牌
   - GET /api/users/                  # 获取用户列表
   - GET /api/users/me/               # 获取当前用户信息

2. 项目相关API
   - GET /api/projects/               # 获取项目列表
   - POST /api/projects/              # 创建新项目
   - GET /api/projects/{id}/          # 获取项目详情
   - PATCH /api/projects/{id}/        # 更新项目信息
   - GET /api/projects/{id}/stats/    # 获取项目统计数据

3. 镜头相关API
   - GET /api/shots/                  # 获取镜头列表(支持筛选和分页)
   - POST /api/shots/                 # 创建新镜头
   - GET /api/shots/{id}/             # 获取镜头详情
   - PATCH /api/shots/{id}/           # 更新镜头状态
   - DELETE /api/shots/{id}/          # 删除镜头
   - GET /api/shots/{id}/history/     # 获取镜头历史记录

4. 反馈相关API
   - GET /api/shots/{id}/comments/    # 获取镜头反馈列表
   - POST /api/shots/{id}/comments/   # 添加反馈
   - PATCH /api/comments/{id}/        # 更新反馈
   - DELETE /api/comments/{id}/       # 删除反馈
   - POST /api/comments/{id}/resolve/ # 标记反馈已解决

5. 附件相关API
   - POST /api/attachments/upload/    # 上传附件
   - GET /api/attachments/{id}/       # 获取附件
   - DELETE /api/attachments/{id}/    # 删除附件

6. 同步相关API
   - POST /api/sync/cgtw/manual/      # 手动触发同步
   - GET /api/sync/logs/              # 获取同步日志
```

#### 3.3 WebSocket实时更新
- 使用Django Channels实现WebSocket服务
- 构建消息格式和序列化机制
- 实现断线重连和心跳检测
- 配置消息分组和广播机制

#### 3.4 CGTeamwork集成模块
- 封装CGTeamwork API调用层
- 实现数据映射和转换逻辑
- 构建增量同步算法
- 实现Celery定时任务

```python
# cgteamwork_sync.py 示例
@shared_task(bind=True, max_retries=3)
def sync_shots_from_cgteamwork(self, project_id=None):
    try:
        # 获取上次同步时间
        last_sync = SyncLog.objects.filter(
            sync_type='shots', 
            status='success'
        ).order_by('-end_time').first()
        
        last_sync_time = last_sync.end_time if last_sync else None
        
        # 创建同步日志
        sync_log = SyncLog.objects.create(
            sync_type='shots',
            start_time=timezone.now(),
            status='in_progress'
        )
        
        # 从CGTeamwork获取数据
        cgtw_client = CGTWClient()
        filters = {'update_time': {'$gt': last_sync_time}} if last_sync_time else {}
        
        if project_id:
            filters['project_id'] = project_id
            
        shots_data = cgtw_client.get_shots(filters)
        
        # 同步数据
        synced_count = 0
        for shot_data in shots_data:
            project = Project.objects.get(cgtw_project_id=shot_data['project_id'])
            
            shot, created = Shot.objects.update_or_create(
                cgtw_task_id=shot_data['id'],
                defaults={
                    'project': project,
                    'shot_code': shot_data['code'],
                    'status': map_status(shot_data['status']),
                    'deadline': parse_date(shot_data['deadline']),
                    'metadata': shot_data
                }
            )
            synced_count += 1
            
        # 更新同步日志
        sync_log.end_time = timezone.now()
        sync_log.status = 'success'
        sync_log.items_synced = synced_count
        sync_log.save()
        
        return f"成功同步 {synced_count} 个镜头"
        
    except Exception as e:
        # 记录错误并重试
        sync_log.status = 'failed'
        sync_log.error_message = str(e)
        sync_log.end_time = timezone.now()
        sync_log.save()
        
        # 发送邮件通知
        send_sync_error_notification(str(e))
        
        # 重试任务
        raise self.retry(exc=e, countdown=60*5)  # 5分钟后重试
```

#### 3.5 错误处理与日志记录
- 实现全局异常处理中间件
- 配置结构化日志记录
- 设计API错误响应格式
- 实现通知机制

### 四、前端开发 (4周)

#### 4.1 用户界面设计
- 制定UI设计规范和组件库
- 实现响应式布局和主题系统
- 设计关键界面原型

#### 4.2 状态看板实现
- 使用Vue3组合式API实现状态分组
- 集成拖拽库实现交互
- 实现状态变更的乐观更新
- 处理并发冲突的解决方案

```javascript
// useShotBoard.js 示例
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '@/composables/useWebSocket'
import { useProjectStore } from '@/stores/project'
import shotService from '@/services/shotService'

export function useShotBoard(projectId) {
  const shots = ref([])
  const loading = ref(true)
  const error = ref(null)
  const projectStore = useProjectStore()
  
  // 按状态分组
  const shotsByStatus = computed(() => {
    const grouped = {
      'in_progress': [],
      'review': [],
      'approved': [],
      'need_revision': []
    }
    
    shots.value.forEach(shot => {
      if (grouped[shot.status]) {
        grouped[shot.status].push(shot)
      } else {
        grouped['in_progress'].push(shot)
      }
    })
    
    return grouped
  })
  
  // 加载镜头数据
  const loadShots = async () => {
    loading.value = true
    try {
      const response = await shotService.getShots({ project_id: projectId })
      shots.value = response.data
    } catch (err) {
      error.value = '加载镜头数据失败'
      console.error(err)
    } finally {
      loading.value = false
    }
  }
  
  // 更新镜头状态
  const updateShotStatus = async (shotId, newStatus) => {
    // 乐观更新
    const shotIndex = shots.value.findIndex(s => s.id === shotId)
    if (shotIndex > -1) {
      const oldStatus = shots.value[shotIndex].status
      shots.value[shotIndex].status = newStatus
      
      try {
        await shotService.updateShot(shotId, { status: newStatus })
      } catch (err) {
        // 恢复原状态
        shots.value[shotIndex].status = oldStatus
        error.value = '更新状态失败'
        console.error(err)
      }
    }
  }
  
  // WebSocket实时更新
  const { connect, disconnect, subscribe } = useWebSocket()
  
  onMounted(() => {
    loadShots()
    
    // 连接WebSocket
    connect()
    
    // 订阅项目更新
    subscribe(`project.${projectId}`, (message) => {
      if (message.type === 'shot_update') {
        const updatedShot = message.data
        const index = shots.value.findIndex(s => s.id === updatedShot.id)
        
        if (index > -1) {
          shots.value[index] = { ...shots.value[index], ...updatedShot }
        } else {
          shots.value.push(updatedShot)
        }
      }
    })
  })
  
  onUnmounted(() => {
    disconnect()
  })
  
  return {
    shots,
    shotsByStatus,
    loading,
    error,
    updateShotStatus,
    refresh: loadShots
  }
}
```

#### 4.3 反馈系统实现
- 支持Markdown格式的反馈内容
- 实现@用户提及功能
- 支持图片/视频附件上传
- 集成实时通知系统

#### 4.4 数据可视化模块
- 实现项目进度仪表盘
- 设计镜头状态统计图表
- 构建反馈解决率分析

### 五、测试与质量保障 (2周)

#### 5.1 测试策略
- 单元测试：80%代码覆盖率
- 集成测试：关键流程测试
- E2E测试：核心用户场景测试
- 性能测试：API响应时间和并发能力

#### 5.2 测试自动化
- 配置CI/CD管道(GitHub Actions)
- 集成测试覆盖率报告
- 设置代码质量检查(pylint/eslint)

### 六、部署与运维 (1周)

#### 6.1 部署架构
```
生产环境部署架构:

                   +----------------+
                   |   负载均衡器   |
                   +-------+--------+
                           |
         +----------------+v+----------------+
         |                 |                 |
+--------v--------+ +------v-------+ +------v-------+
|  Web服务器1     | |  Web服务器2  | |  Web服务器3  |
| (Django+Gunicorn)| |              | |              |
+--------+--------+ +------+-------+ +------+-------+
         |                 |                 |
         +-----------------v-----------------+
                           |
                  +--------v--------+
                  |   PostgreSQL    |
                  | (主/从复制)     |
                  +--------+--------+
                           |
                  +--------v--------+
                  |      Redis      |
                  | (集群模式)      |
                  +-----------------+
```

#### 6.2 监控与告警
- 配置Prometheus + Grafana监控系统
- 设置关键指标告警阈值
- 实现日志聚合和分析(ELK)

#### 6.3 备份与恢复
- 数据库定时备份策略
- 媒体文件异地备份
- 灾难恢复演练计划

### 七、迭代规划与持续改进 (持续)

#### 7.1 MVP后迭代计划
- 第二迭代：高级筛选和搜索功能
- 第三迭代：移动端适配优化
- 第四迭代：批量操作和自动化规则

#### 7.2 性能优化路线图
- 实现数据库查询缓存
- 优化前端资源加载
- 引入CDN加速静态资源

## 总结

本开发计划在原文档基础上进行了全面细化和优化，提供了更为详尽的：
1. 数据库模型设计
2. 完整API端点规范
3. 清晰的项目时间线
4. 详细的开发步骤与示例代码
5. 具体的部署架构与运维方案

通过遵循此计划，项目团队可以更加系统化、条理清晰地推进开发工作，有效控制风险，确保项目质量。


PostgreSQL: postgres:14
Redis: redis:alpine
Python: python:3.10-slim
Node.js: node:18-alpine