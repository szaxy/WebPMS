# 荷和年动画项目管理平台 (WebPMS)

## 项目简介

荷和年动画项目管理平台是一个集成了项目管理、镜头跟踪和反馈系统的全栈Web应用，旨在提升动画制作团队的协作效率。系统与CGTeamwork无缝集成，提供直观的状态看板和实时反馈功能。

## 技术栈

- **后端**: Django 4.x + Django REST Framework + Channels + Celery
- **前端**: Vue 3 + Pinia + Element Plus
- **数据库**: PostgreSQL
- **缓存/消息队列**: Redis
- **部署**: Docker + Nginx + Gunicorn

## 开发环境搭建

### 前提条件

- Docker 和 Docker Compose
- Git

### 安装步骤

1. 克隆代码库

```bash
git clone <repository-url>
cd WebPMS
```

2. 配置环境变量

复制`.env.example`文件为`.env`，并根据实际情况修改环境变量。

```bash
cp .env.example .env
```

3. 启动Docker容器

```bash
docker-compose up -d
```

4. 创建超级用户（首次运行时）

```bash
docker-compose exec backend python manage.py createsuperuser
```

5. 访问应用

- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api
- API文档: http://localhost:8000/swagger/
- 管理后台: http://localhost:8000/admin/

## 主要功能

- 用户认证与权限管理
- 项目与镜头管理
- 状态看板（可拖拽更新）
- 镜头反馈系统
- 用户提及与通知
- CGTeamwork数据同步
- 数据统计与可视化

## 开发指南

### 后端开发

1. 创建新应用

```bash
docker-compose exec backend python manage.py startapp new_app
```

2. 运行测试

```bash
docker-compose exec backend python manage.py test
```

### 前端开发

1. 安装新依赖

```bash
docker-compose exec frontend npm install <package-name>
```

2. 构建生产版本

```bash
docker-compose exec frontend npm run build
```

## 部署指南

详细的部署指南请参见`docs/deployment.md`文件。

## 贡献指南

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 LICENSE 文件 