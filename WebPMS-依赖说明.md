# WebPMS项目依赖与配置说明

## 1. 项目概述

荷和年动画项目管理平台(WebPMS)是一个基于前后端分离架构的项目管理工具，主要用于动画制作流程中的任务跟踪和协作。

## 2. 系统要求

- **操作系统**: Windows 10/11 或 Linux
- **Docker**: 20.10.x 或更高版本
- **Docker Compose**: 2.x 或更高版本
- **存储空间**: 至少5GB可用空间
- **内存**: 至少4GB RAM

## 3. 核心依赖清单

### 3.1 Docker镜像

| 镜像名称 | 版本 | 用途 |
|---------|------|------|
| postgres | 14.15 | 数据库服务 |
| redis | alpine | 缓存和消息队列 |
| python | 3.10-slim | 后端运行环境 |
| node | 18-alpine | 前端运行环境 |

### 3.2 后端依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| Django | 4.2.7 | Web框架 |
| djangorestframework | 3.14.0 | REST API框架 |
| psycopg2-binary | 2.9.5 | PostgreSQL适配器 |
| django-cors-headers | 4.3.0 | 跨域支持 |
| djangorestframework-simplejwt | 5.3.0 | JWT认证 |
| channels | 4.0.0 | WebSocket支持 |
| channels-redis | 4.1.0 | Redis通道层 |
| celery | 5.3.4 | 异步任务队列 |
| redis | 5.0.1 | Redis客户端 |
| gunicorn | 21.2.0 | WSGI HTTP服务器 |
| pillow | 10.0.1 | 图像处理 |
| tomli | 2.0.0 | TOML解析 |

### 3.3 前端依赖

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| vue | 3.3.4 | 前端框架 |
| pinia | 2.1.6 | 状态管理 |
| vite | 4.4.9 | 构建工具 |
| axios | 1.5.0 | HTTP客户端 |
| element-plus | 2.3.12 | UI组件库 |
| @element-plus/icons-vue | 2.1.0 | 图标库 |
| vue-router | 4.2.4 | 路由管理 |
| date-fns | 2.30.0 | 日期处理 |
| lodash | 4.17.21 | 工具函数库 |

## 4. 目录结构

```
WebPMS/
├── backend/              # Django后端代码
├── frontend/             # Vue前端代码
├── docker/               # Docker相关配置
│   └── images/           # 离线Docker镜像
├── offline-resources/    # 离线资源
│   ├── python-packages/  # Python离线包
│   └── npm-packages/     # NPM离线包
├── docker-compose.postgres.yml  # Docker Compose配置
├── start-webpms.bat      # 启动脚本(原始版)
├── start-webpms-optimized.bat  # 优化的启动脚本
└── download-dependencies.bat    # 依赖下载脚本
```

## 5. 离线部署说明

### 5.1 下载依赖

1. 运行`download-dependencies.bat`脚本下载所有必要的依赖
2. 脚本将下载：
   - Python包到`offline-resources/python-packages/py3/`
   - NPM包到`offline-resources/npm-packages/`
   - Docker镜像到`docker/images/`

### 5.2 启动项目

1. 确保Docker Desktop已启动(Windows环境)
2. 运行`start-webpms-optimized.bat`启动项目
3. 脚本将自动：
   - 加载离线Docker镜像
   - 挂载离线依赖包
   - 启动所有必要容器
   - 运行数据库迁移
   - 检查服务健康状态

### 5.3 常见问题

1. **前端连接后端失败**：
   - 检查后端容器是否正常运行
   - 检查后端API是否可通过`http://localhost:8000/api/`访问
   - 查看前端日志：`docker-compose logs frontend`

2. **缺少依赖**：
   - 重新运行`download-dependencies.bat`获取完整依赖
   - 检查各离线资源目录是否正确创建

3. **数据库迁移失败**：
   - 查看后端日志：`docker-compose logs backend`
   - 可能需要手动解决冲突的迁移

4. **内存不足**：
   - 增加Docker可用内存限制
   - 关闭其他占用内存的应用

## 6. 开发注意事项

1. 前端代码修改会自动热重载
2. 后端代码修改需要重启后端容器或使用Django的开发服务器自动重载
3. 添加新的依赖时，需要更新离线资源
4. 更新Docker镜像版本时，需重新下载并保存镜像

## 7. 安全建议

1. 不要在生产环境使用DEBUG模式
2. 定期更新依赖以修复安全漏洞
3. 数据库凭据应通过环境变量注入
4. 生产环境应使用HTTPS配置 